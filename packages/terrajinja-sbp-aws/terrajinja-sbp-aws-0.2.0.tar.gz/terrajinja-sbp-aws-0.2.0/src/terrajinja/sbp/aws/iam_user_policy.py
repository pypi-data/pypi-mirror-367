from cdktf import Fn
from cdktf_cdktf_provider_aws.iam_user_policy import IamUserPolicy
from constructs import Construct


class SbpAwsIamUserPolicy(IamUserPolicy):
    """SBP version of vault.kv_secret_v2"""

    def __init__(self, scope: Construct, ns: str, policy: dict, **kwargs):
        """Enhances the original vault.kv_secret_v2

        Args:
            scope (Construct): Cdktf App
            id (str): uniq name of the resource
            data (dict): a dictionary with the key/values of the secret to store

        Original:
            https://registry.terraform.io/providers/hashicorp/vault/latest/docs/resources/kv_secret_v2
        """

        # policy = {
        #     "Version": "2012-10-17",
        #     "Statement": [
        #         {
        #             "Effect": "Allow",
        #             "Action": [
        #                 "s3:ListBucket",
        #                 "s3:GetBucketLocation",
        #                 "s3:ListBucketMultipartUploads"
        #             ],
        #             "Resource": ["arn:aws:s3:::sapphire-test-log"]
        #         },
        #         {
        #             "Effect": "Allow",
        #             "Action": [
        #                 "s3:PutObject",
        #                 "s3:GetObject",
        #                 "s3:DeleteObject",
        #                 "s3:ListMultipartUploadParts",
        #                 "s3:AbortMultipartUpload"
        #             ],
        #             "Resource": ["arn:aws:s3:::sapphire-test-log/*"]
        #         }
        #     ]
        # }
        #
        # call the original resource
        super().__init__(
            scope=scope,
            id_=ns,
            policy=Fn.jsonencode(policy),
            **kwargs,
        )
