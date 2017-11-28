#!/bin/bash
set -e
cat cloudformation.json | jq
make target/cloudwatch_humio.zip
aws s3 cp --acl public-read cloudformation.json s3://humio-public-us-east-1/
aws s3 cp --acl public-read cloudformation.json s3://humio-public-us-east-2/
aws s3 cp --acl public-read cloudformation.json s3://humio-public-eu-central-1/
aws s3 cp --acl public-read target/cloudwatch_humio.zip s3://humio-public-eu-central-1/
aws s3 cp --acl public-read target/cloudwatch_humio.zip s3://humio-public-us-east-1/
aws s3 cp --acl public-read target/cloudwatch_humio.zip s3://humio-public-us-east-2/
