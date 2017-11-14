import boto3
import gzip
import json
import os
import helpers

def lambda_handler(event, context):
    
    # setup log client
    log_client = boto3.client('logs')

    # grab log group name from incoming event
    log_group_name = event['detail']['requestParameters']['logGroupName'] 

    # env vars 
    humio_log_ingester_arn = os.environ['humio_log_ingester_arn']
    humio_subscription_prefix = os.environ['humio_subscription_prefix']
  
    # check if the prefix is empty
    if not humio_subscription_prefix:
        helpers.create_subscription(log_client, log_group_name, humio_log_ingester_arn, context)

    else:
        # check if log group name starts with our prefix
        if log_group_name.startswith(humio_subscription_prefix):
            helpers.create_subscription(log_client, log_group_name, humio_log_ingester_arn, context)
