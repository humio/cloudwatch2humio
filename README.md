# CloudWatch2Humio
This repository contains a set of lambdas for shipping Cloudwatch Logs and Metrics to Humio.

The full documentation regarding installing and using this integration can be found in the official [humio docs](https://docs.humio.com/integrations/platforms/aws-cloudwatch/).

## Requirements
The *EnableCloudWatchLogsAutoSubscription* option of the integration requires that a CloudTrail is configured, and will create this trail if enabled. This trail keeps a log of all of an AWS account's activity and delivers this data to a S3 bucket, which also will be created. It is important to notice that one trail is free, so if a CloudTrail is already configured for the account, then this will be an additional cost.

## Vision
The vision for the CloudWatch to Humio integration, is to create a bridge between Humio and AWS, which enables users to ingest logs and metrics from the AWS CloudWatch service, so that Humio can be used to manage this data.

## Governance
This project is maintained by employees at Humio ApS.
As a general rule, only employees at Humio can become maintainers and have commit privileges to this repository.
Therefore, if you want to contribute to the project, which we very much encourage, you must first fork the repository.
Maintainers will have the final say on accepting or rejecting pull requests.
As a rule of thumb, pull requests will be accepted if:

   * The contribution fits with the project's vision
   * All automated tests have passed
   * The contribution is of a quality comparable to the rest of the project

The maintainers will attempt to react to issues and pull requests quickly, but their ability to do so can vary.
If you haven't heard back from a maintainer within 7 days of creating an issue or making a pull request, please feel free to ping them on the relevant post.

Maintainers will also be in charge of both versioning and publishing future releases of the project. This includes adding versioning tags and adding to the changelog file.

The active maintainers involved with this project include:

   * [Suzanna Volkov](https://github.com/Suzanna-Volkov)
