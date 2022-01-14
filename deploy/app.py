#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.batch import BatchStack
from stacks.monitoring import MonitoringStack
from stacks.s3_trigger import S3TriggerStack
from stacks.shared import SharedStack

app = cdk.App()

# Create the shared resources (VPC and S3 bucket)
shared = SharedStack(app, "shared")

# Initialise the AWS Batch env and job definition
batch_stack = BatchStack(app, "batch", vpc=shared.vpc)
batch_stack.add_dependency(shared)

# Create a Lambda to trigger AWS Batch on creation of object in the bucket
trigger = S3TriggerStack(app, "s3")
trigger.add_dependency(batch_stack)
trigger.add_dependency(shared)

# Add SNS monitoring stack for Batch failures
monitoring = MonitoringStack(app, "monitor")
monitoring.add_dependency(batch_stack)

app.synth()
