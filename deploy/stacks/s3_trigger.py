from aws_cdk import Stack
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_notifications
from constructs import Construct


class S3TriggerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create lambda function
        self.function = lambda_.Function(
            self,
            f"{id}-lambda-batch-trigger",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="handler.main",
            code=lambda_.Code.from_asset("./lambda"),
        )

        # create s3 bucket
        self.bucket = s3.Bucket(self, f"{id}-s3bucket")

        # create s3 notification for lambda function
        notification = aws_s3_notifications.LambdaDestination(self.function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        self.bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
