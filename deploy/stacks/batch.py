from aws_cdk import Stack
from aws_cdk import aws_batch_alpha as batch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class BatchStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the job definition for the container that will do the conversion
        self.batch_job_definition = batch.JobDefinition(
            self,
            f"{construct_id}-job-definition",
            container=batch.JobDefinitionContainer(
                image=ecs.ContainerImage.from_asset("../convert"),
                vcpus=1,
                memory_limit_mib=2048,
                execution_role=fargate_task_execution_role,
            ),
            platform_capabilities=[batch.PlatformCapabilities.FARGATE],
        )

        # TODO allow Batch r/w access to the S3 bucket
        # bucket = s3.Bucket.from_bucket_arn(
        #     scope=self,
        #     id=f"{construct_id}-s3-bucket",
        #     bucket_arn=ssm.StringParameter.value_for_string_parameter(self, "s3-bucket-arn"),
        # )
        # bucket.grant_read_write(self.batch_instance_role)

        # Create a Fargate backed compute environment for AWS Batch
        # TODO need to ensure this compute environment is setup correctly
        # Lambda rasies this error when trying to submit a job
        # [ERROR] ClientException: An error occurred (ClientException) when calling the SubmitJob operation:
        # Job Queue is attached to Compute Environment that can not run Jobs with capability EC2
        # Traceback (most recent call last):
        # File "/var/task/handler.py", line 29, in main
        #     response = boto3.client("batch").submit_job(
        # File "/var/runtime/botocore/client.py", line 386, in _api_call
        #     return self._make_api_call(operation_name, kwargs)
        # File "/var/runtime/botocore/client.py", line 705, in _make_api_call
        #     raise error_class(parsed_response, operation_name)
        self.compute_environment = batch.ComputeEnvironment(
            self,
            f"{construct_id}-batch-compute-environment",
            compute_resources=batch.ComputeResources(
                vpc=vpc,
                type=batch.ComputeResourceType.FARGATE,
            ),
        )

        # Create the Job Queue for Batch
        self.job_queue = batch.JobQueue(
            self,
            f"{construct_id}-job-queue",
            priority=1,
            compute_environments=[
                batch.JobQueueComputeEnvironment(compute_environment=self.compute_environment, order=1)
            ],
        )

        # Use AWS Systems Manager to store the Job Queue and Job Definition names
        # These are then resolved by the S3 Trigger Stack so the Lambda trigger
        # knows where to send the job
        ssm.StringParameter(
            self,
            f"{construct_id}-job-queue-ref",
            parameter_name="batch-job-queue",
            string_value=self.job_queue.job_queue_name,
            description="AWS Batch Job Queue Name",
        )

        ssm.StringParameter(
            self,
            f"{construct_id}-job-defn-ref",
            parameter_name="batch-job-definition",
            string_value=self.batch_job_definition.job_definition_name,
            description="AWS Batch Job Definition Name",
        )
