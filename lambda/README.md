# `lamda.handler`

This Lambda handler will run in AWS Python Lambda runtime when objects with ".tif[f]" file extension are created in the CDK created "input" S3 bucket.

The lambda handler simply triggers an AWS batch job (that runs [`s3-to-cog](../convert/scripts/s3-to-cog)) setting up the correct environment variables, which are:

* `INPUT_S3_BUCKET`: Pulled out of the S3 trigger event
* `INPUT_S3_KEY`: Pulled out of the S3 trigger event
* `OUTPUT_S3_BUCKET`: Set by CDK to the output S3 bucket it created
* `OUTPUT_S3_KEY`: Set by CDK to the output S3 bucket it created
* `BATCH_JOB_DEFINITION`: Set by CDK to point to AWS Batch resources it created
* `BATCH_JOB_QUEUE`: Set by CDK to point to AWS Batch resources it created