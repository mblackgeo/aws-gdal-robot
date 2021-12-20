#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.s3_trigger import S3TriggerStack

app = cdk.App()
S3TriggerStack(app, "S3TriggerStack")

app.synth()
