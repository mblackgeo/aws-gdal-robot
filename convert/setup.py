from setuptools import find_packages, setup

setup(
    name="convert",
    version="0.1.0",
    url="https://github.com/mblackgeo/aws-gdal-robot.git",
    author="Martin Black",
    author_email="mblack@sparkgeo.com",
    description="A simple GDAL converter that pulls from S3",
    packages=find_packages(),
    install_requires=["boto3", "rasterio", "rio-cogeo"],
)
