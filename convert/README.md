# `convert` - S3 to COG

A python package that provides helper functions for converting a GDAL readable file from S3 to Cloud Optimised Geotiff (using Rasterio and rio-cogeo).

GDAL does not properly respect the S3 Credential Provider Chain, so it will not be able to use IAM roles in services such as ECS or EKS, where there is no access to the magic EC2 endpoint for generating tokens. One workaround for this is set AWS_ACCESS|SECRET_KEY environment variables when running such services in ECS/EKS, however this is not desriable as a new keys / roles would have to created and managed with appropriate credential cycling and the possiblity of these keys being leaked, hence it is preferred to simply use the IAM role that the service is running with. To achieve this, this package uses boto3 with some helper functions for reading/writing bytes directly from S3 into an in memory dataset.

## Usage

The main entry point for the package is the [`s3-to-cog`](./scripts/s3-to-cog) script. For now, this simply requires the environment variables to be set as follows:

* `INPUT_S3_BUCKET` : Name of S3 bucket with input data
* `INPUT_S3_KEY` : Path to GDAL image in the input bucket
* `OUTPUT_S3_BUCKET` : Name of output S3 bucket
* `OUTPUT_S3_KEY` : Path to store the output COG

The script can also be run in the provided in a docker container; see [build](build.sh) and [local](local.sh) scripts for usage.

## Development

Create a new virtual env, install the requirements:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

Additionally, a docker image is provided (that will run in AWS Batch). This image can be built and run as follows:

```shell
# build the docker image and install the package
./build.sh

# sign into the Sparkgeo UK account and ensure AWS credentials are valid
aws sso login --profile sparkgeouk
cdk-sso-sync --profile sparkgeouk

# run the image locally to convert a small test image in S3
./local.sh

# alternatively for debugging, drop into an interactive shell in the container
./local.sh --debug
```