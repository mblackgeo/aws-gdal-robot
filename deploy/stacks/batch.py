from aws_cdk import Stack
from aws_cdk import aws_batch_alpha as batch
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from constructs import Construct


class BatchStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        s3_stack: Stack,
        networking_stack: Stack,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a service role for AWS Batch
        self.batch_service_role = iam.Role(
            self,
            f"{id}-BatchServiceRole",
            assumed_by=iam.ServicePrincipal("batch.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBatchServiceRole"
                )
            ],
        )

        # Create a role for Batch in Fargate
        self.batch_ecs_role = iam.Role(
            self,
            f"{id}-BatchFargateRole",
            assumed_by=iam.ServicePrincipal("ecs.amazonaws.com"),
        )

        # Allow the compute role to access to S3
        s3_stack.bucket.grant_read_write(self.batch_ecs_role)

        # compute environment backed by Fargate
        fargate_spot_environment = batch.ComputeEnvironment(
            self,
            "MyFargateEnvironment",
            compute_resources=batch.ComputeResources(
                type=batch.ComputeResourceType.FARGATE, vpc=networking_stack.vpc
            ),
        )

        # job queue
        batch.JobQueue(
            self,
            f"{id}-BatchQueue",
            compute_environments=[
                batch.JobQueueComputeEnvironment(
                    compute_environment=fargate_spot_environment, order=1
                )
            ],
            priority=1,
        )

        # job definition
        batch.JobDefinition(
            self,
            f"{id}-BatchJob",
            container=batch.JobDefinitionContainer(
                image=ecs.ContainerImage.from_asset("../convert"),
                vcpus=1,
                memory_limit_mib=2048,
            ),
        )
