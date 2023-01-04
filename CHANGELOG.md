# Changelog

## 2.0.0 (2023-01-03)
Updated naming where possible to LogScale.
Added functionality to choose which S3 bucket should be used for 
retrieving the code files for the AWS Lambda functions, 
removed the option to choose older versions of the integration,
and replaced the name Humio with LogScale where possible.


### Added
- Introduced parameter groups in the CF template.
- Added parameter for setting the S3 bucket containing the Lambda code files.
- Added parameter for setting the S3 key in the S3 bucket containing the Lambda code files.
- Created resources for copying the Lambda code files from the specified S3 bucket, so that it is no longer required to create a new bucket in each region supported. The default S3 bucket hosted by Humio is named _humio-public-us-east-1_.
- Added a parameter for determining whether the CloudTrail and S3 bucket for autosubscription should be created, which also made it possible to delete the additional CF template.
- Added it possible for users to set which S3 bucket they want to retrieve the Lambda code files from, which also made it possible to delete the CF template for testing.


### Changed
- Made metric ingester and metric statistics ingester creation optional.
- Updated the README of the project to contain a section concerning how the integration works.
- Updated the deployment scripts. 
- Replaced 'Humio' with 'LogScale' where possible. 

### Removed
- Removed the CF template with no trail.
- Removed the CF template for testing.
- Removed the parameter related to versions, so that there is only the newest version of the code uploaded.

## 1.2.2 (2022-08-30)
Added additional login at ingest error.

### Added
- Logging for when ingest into Humio fails.

## 1.2.1 (2021-01-12)
Performance regression fix.

### Changed
- A setup function has now been scoped properly and will thus not be called unnecessarily, which affected performance time.

## 1.2.0 (2020-11-03)
Added retention parameter for the lambdas.

### Added
- A parameter in the CF file has been added so that retention can be set for the lambdas.

## 1.1.0 (2020-11-03)
Added logging library to allow debug logs to be ignored.

### Added
- The logging library has been added to all files with print functions to allow users to determine what level of logs they want logged by the lambdas.

### Changed
- Versioning has been made a dropdown with available options.

## 1.0.0 (2020-09-08)
Versioning added for a more seamless flow for updating the integration..

### Added
- Support for updating an integration to its newest version.
- Bump2version configuration file for maintaining the integration version.
- Version parameter in the CloudFormation file.
- Section describing how to release a new version for maintainers.

### Changed
- Guide for setting up the integration for local development.
- Name of the generated ZIP file containing the lambdas.

## (2020-07-13)
CloudFormation updated to support using an AWS VPC for lambda ingesters and for the backfiller to be able to be run automatically when created.

### Added
- Support for using a VPC regarding lambda ingesters based on a conditional set.
- Support for automatically running the backfiller lambda when created based on a conditional set.

### Changed
- Parameter and resource names in the CloudFormation file.
- Formatting.

### Removed
- Unused environment variables in the CloudFormation file.
- Unused library.

## (2020-06-11)
Major refactoring of codebase and new feature for retrieving CloudWatch metrics.

### Added
- Support for retrieving CloudWatch metrics using GetMetricData and GetMetricStatistics.
- Consistent code formatting.

### Changed
- Python version to 3.8.
- Humio Ingest API calls to be using the newest endpoints.
- File and function names in the project and CloudFormation file.
- Project structure.

### Removed
- Unused files and functions.
