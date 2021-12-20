import logging
import os
import sys
from io import BytesIO
from uuid import uuid4

import boto3
import rasterio
from osgeo import gdal
from rasterio.io import MemoryFile
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s.%(funcName)s:L%(lineno)d - %(message)s",
    datefmt="%y/%m/%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__file__)


class S3Helper:
    def __init__(self, bucket: str):
        log.info(f"Initialising S3 bucket with boto3 : {bucket}")
        self.bucket = boto3.Session().resource("s3").Bucket(bucket)

    def get_bytes(self, key: str) -> BytesIO:
        """Get a file from S3 using Boto3 returning the binary data"""
        # Download the bytes for the given key to a BytesIO object
        log.info(f"Reading bytes from key : {key}")
        buf = BytesIO()
        self.bucket.download_fileobj(Key=key.lstrip("/"), Fileobj=buf)
        buf.seek(0)
        return buf

    def write_bytes(self, content: BytesIO, key: str) -> None:
        log.info(f"Writing data to S3 : {key}")
        content.seek(0)
        self.bucket.upload_fileobj(
            Key=key.lstrip("/"),
            Fileobj=content,
            ExtraArgs={"ACL": "bucket-owner-full-control"},
        )

    def get_gdal_dataset(self, key: str) -> gdal.Dataset:
        """Read a GDAL Dataset directly from S3"""
        # GDALs virtual file system for S3 does not inherit the provider chain
        # correctly so we cannot use /vsis3/bucket/key outside of EC2
        # See https://github.com/OSGeo/gdal/issues/4058

        # This is a bit of a messy workaround as GDALs python bindings do not
        # open a File/Path like object. Rasterio for example can write directly
        # from ``self.get_bytes()``, so that is probably preferred.
        log.info(f"Loading GDAL Dataset from : {key}")

        # Write bytes to temporary memory file buffer and open that with GDAL
        tmp_fname = f"/vsimem/{uuid4()}"
        gdal.FileFromMemBuffer(tmp_fname, self.get_bytes(key).getvalue())

        log.info(f"Opening GDAL file from memory buffer ({tmp_fname})")
        return gdal.Open(tmp_fname)

    def write_gdal_dataset(self, ds: gdal.Dataset, key: str) -> None:
        # Not implementing this for now, but this is an option for how to write
        # a GDAL dataset from memory to a Bytes object
        # Taken from the OSGeo mailing list
        # gdal.GetDriverByName('PNG').CreateCopy('/vsimem/output.png', mem)

        # # Read /vsimem/output.png
        # f = gdal.VSIFOpenL('/vsimem/output.png', 'rb')
        # gdal.VSIFSeekL(f, 0, 2) # seek to end
        # size = gdal.VSIFTellL(f)
        # gdal.VSIFSeekL(f, 0, 0) # seek to beginning
        # data = gdal.VSIFReadL(1, size, f)
        # gdal.VSIFCloseL(f)

        # # Cleanup
        # gdal.Unlink('/vsimem/output.png')
        pass


def main(bucket: str, key: str, out_bucket: str, out_key: str) -> None:
    """Convert the given S3 bucket/key to Cloud Optimised GeoTiff"""
    # Setup connection to S3 and download the data
    in_s3 = S3Helper(bucket)
    data = in_s3.get_bytes(key)

    # Use rasterio to open the BytesIO as a file
    with rasterio.open(data) as src:
        log.info(f"Opened file. Format is : {src.driver}")

        # Write a converted Cloud Optimised GeoTiff to Bytes
        log.info("Converting to Cloud Optmised GeoTiff")
        dst_profile = cog_profiles.get("deflate")

        with MemoryFile() as mem_dst:
            # convert the src to COG
            cog_translate(src, mem_dst.name, dst_profile, in_memory=True)

            # Write to S3
            out_s3 = S3Helper(out_bucket)
            out_s3.write_bytes(mem_dst, out_key)


if __name__ == "__main__":
    # inputs
    bucket = os.environ.get("INPUT_S3_BUCKET", "sparkgeouk-tmp-eu-west-1")
    key = os.environ.get("INPUT_S3_KEY", "landsat.tif")

    # outputs
    out_bucket = os.environ.get("OUTPUT_S3_BUCKET", bucket)
    out_key = os.environ.get("OUTPUT_S3_KEY", key.replace(".tif", "-cog.tif"))

    main(bucket, key, out_bucket, out_key)
