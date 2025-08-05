# terrajinja-sbp-aws

This is an extension to the vault provider for the following modules.
The original documentation can be found [here](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

# SBP Specific implementations
Here is a list of supported resources and their modifications

## sbp.aws.iam_user_policy
Original provider: [aws.iam_user_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user_policy)

This custom provider adds the following:
- automaticly convert data to json as input for the resource

| old parameter | new parameter | description |
|---------------|---------------| ------ |
| policy        | policy        | the data field is automaticly converted to json |


### terrajinja-cli example
the following is a code snipet you can used in a terrajinja-cli template file.
This creates a s3 policy

```
terraform:
  resources:
    - task: "s3-policy"
      module: sbp.aws.iam_user_policy
      parameters:
        name: "s3-policy"
        user: "$s3-customer-user.name"
        provider: '$aws-provider-cloudian'
        policy:
          Version: "2012-10-17"
          Statement:
            - Effect: "Allow"
              Action:
                - "s3:ListBucket"
                - "s3:GetBucketLocation"
                - "s3:ListBucketMultipartUploads"
              Resource:
                - "arn:aws:s3:::bucket-name"
            - Effect: "Allow"
              Action:
                - "s3:PutObject"
                - "s3:GetObject"
                - "s3:DeleteObject"
                - "s3:ListMultipartUploadParts"
                - "s3:AbortMultipartUpload"
              Resource:
                - "arn:aws:s3:::bucket-name/*"
```

