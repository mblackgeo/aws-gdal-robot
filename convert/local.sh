#!/bin/bash

# Get secrets from AWS credentials
# Note must sign in locally first with `$ aws sso login --profile sparkgeouk`
# Assumes that AWS SSO has already been setup
AWS_ACCESS_KEY_ID="$(cat ~/.aws/credentials | grep sparkgeouk -A 20 | grep aws_access_key | head -n1 | awk -F'=' '{print $2}' | tr -d '[ ]')"
AWS_SECRET_ACCESS_KEY="$(cat ~/.aws/credentials | grep sparkgeouk -A 20 | grep aws_secret_access_key | head -n1 | awk -F'=' '{print $2}' |  tr -d '[ ]')"
AWS_SESSION_TOKEN="$(cat ~/.aws/credentials | grep sparkgeouk -A 20 | grep aws_session_token | head -n1 | awk -F'=' '{print $2}' |  tr -d '[ ]')"

# Setting up args required for both normal running and debug
COMMON_ARGS=(
    -e "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID"
    -e "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY"
    -e "AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN"
    -e "INPUT_S3_BUCKET=sparkgeouk-tmp-eu-west-1"
    -e "INPUT_S3_KEY=landsat.tif"
    -e "OUTPUT_S3_BUCKET=sparkgeouk-tmp-eu-west-1"
    -e "OUTPUT_S3_KEY=landsat-cog.tif"
    aws-gdal-robot-convert:latest
)

# Running
DEBUG=$(python -c "import sys; print('true') if '--debug' in sys.argv else print('')" $@)
if [[ "$DEBUG" == "true" ]]
then
  docker run -ti ${COMMON_ARGS[@]} /bin/bash
else
  docker run ${COMMON_ARGS[@]}
fi

