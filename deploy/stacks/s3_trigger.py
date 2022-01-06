from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class S3TriggerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the S3 bucket that was created in the Shared Stack
        bucket = s3.Bucket.from_bucket_arn(
            scope=self,
            id=f"{construct_id}-s3-bucket",
            bucket_arn=ssm.StringParameter.value_for_string_parameter(self, "s3-bucket-arn"),
        )

        # Grab the AWS Batch parameters from session manager
        # These are needed by the lambda function to send the AWS Batch job
        job_defn_name = ssm.StringParameter.value_for_string_parameter(self, "batch-job-definition")
        job_queue_name = ssm.StringParameter.value_for_string_parameter(self, "batch-job-queue")

        # Get the output S3 bucket
        out_bucket = s3.Bucket.from_bucket_arn(
            scope=self,
            id=f"{construct_id}-s3-outpuyt-bucket",
            bucket_arn=ssm.StringParameter.value_for_string_parameter(self, f"s3-outpuyt-bucket-arn"),
        )

        # create lambda function that uses the python handler
        # this will trigger the AWS Batch job
        self.function = lambda_.Function(
            self,
            f"{construct_id}-lambda-batch-trigger",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="handler.main",
            code=lambda_.Code.from_asset("../lambda"),
            environment={
                "BATCH_JOB_DEFINITION": job_defn_name,
                "BATCH_JOB_QUEUE": job_queue_name,
                "OUTPUT_S3_BUCKET": out_bucket.bucket_name,
            },
        )

        # Add permission for Lambda to submit a job to AWS Batch
        self.function.role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                scope=self,
                id=f"{construct_id}-batch-policy-arn",
                managed_policy_arn="arn:aws:iam::aws:policy/AWSBatchFullAccess",
            )
        )

        # Create the notification trigger on the S3 bucket that will
        # trigger Lambda when an object is created
        notification = aws_s3_notifications.LambdaDestination(self.function)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
