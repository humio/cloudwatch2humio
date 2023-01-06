import boto3
import os
import helpers

# Set environment variables.
logscale_log_ingester_arn = os.environ["logscale_log_ingester_arn"]
logscale_subscription_prefix = os.environ.get("logscale_subscription_prefix")

# Set up CloudWatch Logs client.
log_client = boto3.client("logs")


def lambda_handler(event, context):
    """
    Subscribes log ingester to log group from event.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # Grab the log group name from incoming event.
    log_group_name = event["detail"]["requestParameters"]["logGroupName"]
  
    # Check whether the prefix is set - the prefix is used to determine which logs we want.
    if not logscale_subscription_prefix:
        helpers.create_subscription(
            log_client, log_group_name, logscale_log_ingester_arn, context
        )

    else:
        # Check whether the log group's name starts with the set prefix.
        if log_group_name.startswith(logscale_subscription_prefix):
            helpers.create_subscription(
                log_client, log_group_name, logscale_log_ingester_arn, context
            )
