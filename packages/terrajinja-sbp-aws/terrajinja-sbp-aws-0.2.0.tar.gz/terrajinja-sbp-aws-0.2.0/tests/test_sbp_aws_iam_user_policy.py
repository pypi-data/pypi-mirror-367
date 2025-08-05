import random

import pytest
from cdktf import Testing

from src.terrajinja.sbp.aws.iam_user_policy import SbpAwsIamUserPolicy
from .helper import stack, has_resource, has_resource_path_value, has_resource_path_value_not_contain


class TestSbpVault:
    def test_json_formatting(self, stack):
        SbpAwsIamUserPolicy(
            scope=stack,
            ns="sbp_aws_iam_user_policy",
            policy={ "Version": "2012-10-17" },
            user="user"
        )

        synthesized = Testing.synth(stack)
        print(synthesized)

        has_resource(synthesized, "aws_iam_user_policy")
        # has_resource_path_value(synthesized, "aws_iam_user_policy", "sbp_aws_iam_user_policy", "policy"
        #                         r'${jsonencode({\"Version\" = \"2012-10-17\"})}')


if __name__ == "__main__":
    pytest.main()
