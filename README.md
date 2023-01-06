# CloudWatch2LogScale
This repository contains a CloudFormation template as well as Python code files for setting up an integration
which is used for shipping Cloudwatch Logs and Metrics to LogScale.

The full documentation regarding installing and using this integration can be found in the official 
[humio library](https://library.humio.com/reference/log-formats/amazon-cloudwatch/).

## Vision
The vision for the CloudWatch to LogScale integration, is to create a bridge between LogScale and AWS,
which enables users to ingest logs and metrics from the AWS CloudWatch service, 
so that LogScale can be used to manage this data.

## Governance
This project is maintained by employees at CrowdStrike.
As a general rule, only employees at CrowdStrike can become maintainers and have commit privileges to this repository.
Therefore, if you want to contribute to the project, which we very much encourage, you must first fork the repository.
Maintainers will have the final say on accepting or rejecting pull requests.
As a rule of thumb, pull requests will be accepted if:

   * The contribution fits with the project's vision
   * All automated tests have passed
   * The contribution is of a quality comparable to the rest of the project

The maintainers will attempt to react to issues and pull requests quickly, but their ability to do so can vary.
If you haven't heard back from a maintainer within 7 days of creating an issue or making a pull request , 
please feel free to ping them on the relevant post.

Maintainers will also be in charge of both versioning and publishing future releases of the project. 
This includes adding versioning tags and adding to the changelog file.

The active maintainers involved with this project include:

   * [Suzanna Volkov](https://github.com/Suzanna-Volkov)

## How this integration works
The integration consists of a CloudFormation template and some Python code files used for lambda functions. 
The lambda code files are zipped and uploaded to a public S3 bucket hosted by LogScale. 
When creating a CloudStack using this CloudFormation template, 
some additional helper resources are created to help copy the lambda code files from the S3 bucket hosting the 
files to a newly created S3 bucket in the user's AWS environment. 
This is so that we do not have to create buckets in each supported region as the CloudFormation has a 
restriction that it can only retrieve lambda code files from a bucket located in the same region as the stack.

When all the resources are created, the lambda functions will start sending logs to the LogScale host, 
which was determined during setup. 
Chosen log groups are subscribed to, and whenever new logs arrive, these will be forwarded to LogScale. 
This means that existing logs will not be forwarded to LogScale using this integration.
To get existing logs into LogScale another approach is required, which will probably include manually downloading
the existing logs and then sending them to LogScale using some sort of shipper. 

## Versioning
Versioning is used for the ZIP package containing the deployment files.
Versioning of the deployment package is required to make it possible to update an already installed
integration's code files.
A CloudStack will only update its files if the name changes, so you cannot use a file with the
same name as is already used to update with as it won't be recognized as a change. 
So to force CloudStack to run an update, the deployment package name needs to be changed. 
This means that only one file version is necessary to maintain in the public S3 bucket, 
but the name needs to be updated every time there are new changes to the code files. 

A flow can be setup where older versions are deleted when a new one is uploaded, this does not yet exist.

It is thus not necessary to make a new release of the integration unless the Python files are changed,
however, changes to the CloudFormation file will still be included in the CHANGELOG. Therefore,
version updates has happened whenever there are changes pushed to the GitHub repository to keep these
two numbers aligned. 

## Adding new regions
The most common request from users is that a new region be supported. Since the move to one bucket in one region,
it is no longer necessary to add new buckets, and thus this code does not need any updates. To support a new region
there simply needs to be added a link in the documentation. 
