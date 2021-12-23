import logging

import rasterio
from rasterio.io import MemoryFile
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

from convert.s3 import S3Helper

log = logging.getLogger(__name__)


def to_cog(bucket: str, key: str, out_bucket: str, out_key: str) -> None:
    """Convert the given S3 bucket/key to Cloud Optimised GeoTiff

    Parameters
    ----------
    bucket : str
        Input S3 bucket
    key : str
        Input S3 key to convert
    out_bucket : str
        Output S3 bucket where COG will be saved
    out_key : str
        Key (filename) of the COG saved in ``out_bucket``
    """
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
