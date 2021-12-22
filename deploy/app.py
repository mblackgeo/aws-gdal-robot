#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.batch import BatchStack
from stacks.s3_trigger import S3TriggerStack
from stacks.shared import SharedStack

app = cdk.App()

# Create the shared resources (VPC and S3 bucket)
shared = SharedStack(app, "SharedStack")

# Initialise the AWS Batch env and job definition
batch_stack = BatchStack(app, "BatchStack", bucket=shared.bucket, vpc=shared.vpc)

# Create a Lambda to trigger AWS Batch on creation of object in the bucket
trigger = S3TriggerStack(app, "S3TriggerStack", bucket=shared.bucket)

app.synth()
