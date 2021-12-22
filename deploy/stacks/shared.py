from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_s3 as s3
from constructs import Construct


class SharedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # basic VPC setup
        self.vpc = ec2.Vpc(
            self,
            f"{construct_id}-vpc",
            cidr="10.0.0.0/16",
            nat_gateways=0,  # TODO check if this is needed
        )

        # create an s3 bucket with no public access
        # this will trigger lambda job -> AWS Batch when a file is created
        self.bucket = s3.Bucket(
            self,
            f"{construct_id}-s3-bucket",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
