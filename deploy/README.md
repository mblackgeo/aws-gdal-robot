## Overview

This CDK project creates an S3 bucket, which triggers a Lambda function when an tiff image item is uploaded, that in turn triggers AWS Batch to convert the tiff to a Cloud Optmised Geotiff. Only file extension filtering is done by the S3 trigger (for .tif[f]) rather than a comprehensive check that the object does indeed contain a valid GDAL readable image.

## Development

This project was created with AWS CDK v2. The `cdk.json` file tells the CDK Toolkit how to execute the app.

A new virtual environment should be created for the infra deployment:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# if this is the first time CDK has been used, your account should be bootstrapped
cdk bootstrap
```

CDK can then be used to deploy:

```shell
# synth the cloud formation template to ensure there are no errors
cdk synth

# check what changes will be made first before deploying
cdk diff

# deploy the stacks
cdk deploy --all  # --require-approval never

# To remove
# Note that CDK cannot yet remove the images stored in ECR so this should
# be done manually
cdk destroy
```

Useful commands:
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation


## A note about AWS SSO

If you are using AWS Single Sign On (SSO), the you should first ensure you are signed in:

```shell
# if this is the first time using the AWS command line, configure SSO:
aws sso configure

# then login to generate access keys
aws sso login
```

However, CDK and AWS SSO are not yet connected. A helper npm package, [cdk-sso-sync](https://www.npmjs.com/package/cdk-sso-sync) can be used to ensure CDK can read your access keys:

```shell
cdk-sso-sync <PROFILE_NAME>
```