#!/bin/bash
set -e
cat cloudformation.json | jq
make build

aws s3 cp --acl public-read cloudformation.json s3://humio-public-us-east-1/ --region us-east-1 --profile cloudwatch
aws s3 cp --acl public-read target/cloudwatch2humio.zip s3://humio-public-us-east-1/ --region us-east-1 --profile cloudwatch

aws s3 cp --acl public-read cloudformation.json s3://logscale-public-us-east-1/ --region us-east-1 --profile cloudwatch
aws s3 cp --acl public-read target/cloudwatch2logscale.zip s3://logscale-public-us-east-1/ --region us-east-1 --profile cloudwatch
