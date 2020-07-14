# Changelog

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
