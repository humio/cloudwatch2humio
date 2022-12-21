#!/bin/bash
set -e
cat cloudformation.json | jq
make build

# It is not necessary to upload the lambda code files to anywhere but the us-east-1 region now as the files
# will be retrieved from there no matter what region the CloudStack.

aws s3 cp --acl public-read cloudformation.json s3://humio-public-us-east-1/ --region us-east-1
#aws s3 cp --acl public-read cloudformation-no-trail.json s3://humio-public-us-east-1/ --region us-east-1

#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-eu-central-1/ --region eu-central-1
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-eu-west-1/ --region eu-west-1
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-eu-west-2/ --region eu-west-2
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-eu-west-3/ --region eu-west-3
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-eu-north-1/  --region eu-north-1

aws s3 cp --acl public-read target/v1.3.0_cloudwatch2humio.zip s3://humio-public-us-east-1/ --region us-east-1
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-us-east-2/ --region us-east-2
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-us-west-2/ --region us-west-2

#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-ap-southeast-1/ --region ap-southeast-1
#aws s3 cp --acl public-read target/v1.2.2_cloudwatch2humio.zip s3://humio-public-ap-southeast-2/ --region ap-southeast-2