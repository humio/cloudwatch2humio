# Changelog

## 1.2.2 (2022-08-30)
Added additional login at ingest error

### Added
- Logging for when ingest into Humio fails

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
