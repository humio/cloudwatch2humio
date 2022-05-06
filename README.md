# CloudWatch2Humio
This repository contains a set of lambdas for shipping Cloudwatch Logs and Metrics to Humio.

The full documentation regarding installing and using this integration can be found in the official [humio library](https://library.humio.com/reference/log-formats/amazon-cloudwatch/).

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

## CloudFormation Files
There are two versions of the CloudFormation file; one which creates a CloudTrail with a S3 bucket for log storage, 
and one which does not create these resources.
The reason for this is that every AWS account only allows for one free CloudTrail, 
and adding another will therefore be an additional cost for setting up this integration if one is already present. 
By introducing two versions of the CloudFormation file, 
it is possible for the user to choose whether they want to create a CloudTrail specifically to be used with this integration, 
or to use a one which already exists.

***It is thus required when creating a stack using the "no-trail" CloudFormation file that an existing CloudTrail with "management events" enabled already to be present for the account!***

The CloudTrail is used by the integration for discovering new log groups in CloudWatch, 
which makes it possible for the integration to automatically subscribe to these when they appear.
This is only done if the parameter `EnableCloudWatchLogsAutoSubscription` is set to **true**.
