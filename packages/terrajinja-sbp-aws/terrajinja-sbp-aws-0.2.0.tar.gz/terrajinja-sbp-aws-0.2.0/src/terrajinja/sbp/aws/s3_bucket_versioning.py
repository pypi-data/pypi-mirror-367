from cdktf_cdktf_provider_aws.s3_bucket_versioning import S3BucketVersioningA
from constructs import Construct


class SbpAwsS3BucketVersioning(S3BucketVersioningA):
    """SBP version of aws.s3_bucket_versioning"""

    def __init__(self, scope: Construct, ns: str, **kwargs):
        """Because import and class do not exactly match

        Args:
            scope (Construct): Cdktf App
            ns (str): namespace

        Original:
            https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning
        """

        # call the original resource
        super().__init__(
            scope=scope,
            id_=ns,
            **kwargs,
        )
