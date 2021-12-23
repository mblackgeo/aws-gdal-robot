import logging
from io import BytesIO
from uuid import uuid4

import boto3
from mypy_boto3_s3.client import S3Client
from osgeo import gdal

log = logging.getLogger(__name__)


class S3Helper:
    """Helper class for reading and writing to S3 using Boto3"""

    def __init__(self, bucket_name: str):
        """Initialise an instance of an S3 Bucket

        Parameters
        ----------
        bucket : str
            Name of S3 bucket
        """
        self.bucket_name = bucket_name
        self.bucket = self._init_bucket()

    def _init_bucket(self) -> S3Client:
        """Initialise the Boto3 S3 client"""
        log.info(f"Initialising S3 bucket with boto3 : {self.bucket_name}")
        return boto3.Session().resource("s3").Bucket(self.bucket_name)

    def get_bytes(self, key: str) -> BytesIO:
        """Get a file from S3 using Boto3 returning the binary data

        Parameters
        ----------
        key : str
            Key to download as bytes

        Returns
        -------
        BytesIO
            Bytes of ``key``
        """
        # Download the bytes for the given key to a BytesIO object
        log.info(f"Reading bytes from key : {key}")
        buf = BytesIO()
        self.bucket.download_fileobj(Key=key.lstrip("/"), Fileobj=buf)
        buf.seek(0)
        return buf

    def write_bytes(self, content: BytesIO, key: str) -> None:
        """Write a BytesIO object to the given key

        Parameters
        ----------
        content : BytesIO
            Bytes to write
        key : str
            Output key (filename)
        """
        log.info(f"Writing data to S3 : {key}")
        content.seek(0)
        self.bucket.upload_fileobj(
            Key=key.lstrip("/"),
            Fileobj=content,
            ExtraArgs={"ACL": "bucket-owner-full-control"},
        )

    def get_gdal_dataset(self, key: str) -> gdal.Dataset:
        """Read a GDAL Dataset directly from S3

        This function helps read a GDAL Dataset directly from S3 by using
        boto3 directly. This has the downside that we cannot intelligently
        stream the data and the entire dataset will be read into memory upfront
        however it does correctly use the S3 provider chain (meaning it can run
        in non-EC2 environments such as EKS or ECS).

        GDALs virtual file system for S3 does not inherit the provider chain
        correctly so we cannot use /vsis3/bucket/key outside of EC2
        See https://github.com/OSGeo/gdal/issues/4058.

        Parameters
        ----------
        key : str
            Name of ley containing a GDAL readable dataset

        Returns
        -------
        gdal.Dataset
            GDAL Dataset in memory
        """
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
        """Write a GDAL dataset to S3

        Parameters
        ----------
        ds : gdal.Dataset
            GDAL dataset to write
        key : str
            Output key (filename)
        """
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
        raise NotImplementedError
