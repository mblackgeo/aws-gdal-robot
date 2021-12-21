#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.batch import BatchStack
from stacks.networking import NetworkingStack
from stacks.s3_trigger import S3TriggerStack

app = cdk.App()

networking = NetworkingStack(app, "NetworkingStack")
s3_stack = S3TriggerStack(app, "S3TriggerStack")
batch_stack = BatchStack(app, "BatchStack", bucket=s3_stack.bucket, vpc=networking.vpc)

app.synth()
