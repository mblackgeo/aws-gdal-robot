from aws_cdk import Stack
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as events_targets
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subscriptions
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class MonitoringStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an SNS topic to hold the job failures
        topic = sns.Topic(
            self,
            f"{construct_id}-batch-job-failed",
            display_name="S3-to-COG failures topic",
            topic_name="s3-to-cog-failures",
        )

        topic.add_subscription(
            subscriptions.EmailSubscription("mblack@sparkgeo.com")
        )  # TODO move email address to config

        # Create a pattern that will match AWS Batch failures
        job_defn_name = ssm.StringParameter.value_for_string_parameter(self, "batch-job-definition")
        pattern = events.EventPattern(
            source=["aws.batch"],
            detail={"status": ["FAILED"], "jobDefinition": [f"{job_defn_name}*"]},
            detail_type=["Batch Job State Change"],
        )

        # Register an Event Rule to capture the AWS Batch failures and post to SNS
        events.Rule(
            self,
            f"{construct_id}-batch-failed-event-rule",
            description="",
            event_pattern=pattern,
            targets=[events_targets.SnsTopic(topic=topic)],
        )
