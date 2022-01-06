from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class SharedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ---------------------------------------------------------------------
        # VPC
        # ---------------------------------------------------------------------
        # basic VPC setup
        self.vpc = ec2.Vpc(
            self,
            f"{construct_id}-vpc",
            cidr="10.0.0.0/16",
            nat_gateways=0,  # Using VPC endpoints to save $
        )

        # Build VPC endpoints to access AWS services without using NAT Gateway.
        # Allow ECS to pull Docker images without using NAT Gateway
        # https://docs.aws.amazon.com/AmazonECR/latest/userguide/vpc-endpoints.html
        endpoints = {
            "ecr_docker": ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            "ecr": ec2.InterfaceVpcEndpointAwsService.ECR,
            "secrets_manager": ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            "cloudwatch": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            "cloudwatch_logs": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            "cloudwatch_events": ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS,
            "ssm": ec2.InterfaceVpcEndpointAwsService.SSM,
        }

        for name, service in endpoints.items():
            endpoint = self.vpc.add_interface_endpoint(f"{construct_id}-endpoint-{name}", service=service)
            endpoint.connections.allow_from(ec2.Peer.ipv4(self.vpc.vpc_cidr_block), endpoint.connections.default_port)

        self.vpc.add_gateway_endpoint(f"{construct_id}-gateway-s3", service=ec2.GatewayVpcEndpointAwsService.S3)

        # ---------------------------------------------------------------------
        # S3
        # ---------------------------------------------------------------------
        # create an input/output s3 buckets with no public access
        # the input bucket will trigger lambda job to run AWS Batch when a file
        # is created
        for btype in ["input", "output"]:
            # create the buket
            # TODO - deletion policy
            bucket = s3.Bucket(
                self,
                f"{construct_id}-s3-{btype}-bucket",
                public_read_access=False,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            )

            # Store the bucket in Session Manager for other stacks to use
            ssm.StringParameter(
                self,
                f"{construct_id}-s3-{btype}-bucket-ref",
                parameter_name=f"s3-{btype}-bucket-arn",
                string_value=bucket.bucket_arn,
                description=f"S3 {btype} bucket ARN",
            )
