import boto3
import os
import helpers

# Set environment variables.
humio_log_ingester_arn = os.environ["humio_log_ingester_arn"]
humio_subscription_prefix = os.environ.get("humio_subscription_prefix")

# Set up CloudWatch Logs client.
log_client = boto3.client("logs")


def lambda_handler(event, context):
    """
    Auto-subscribe to log group from event.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda object context.
    :type context: obj

    :return: None
    :rtype: NoneType
    """
    # Grab the log group name from incoming event.
    log_group_name = event["detail"]["requestParameters"]["logGroupName"]
  
    # Check whether the prefix is set - the prefix is used to determine which logs we want.
    if not humio_subscription_prefix:
        helpers.create_subscription(
            log_client, log_group_name, humio_log_ingester_arn, context
        )

    else:
        # Check whether the log group's name starts with the set prefix.
        if log_group_name.startswith(humio_subscription_prefix):
            helpers.create_subscription(
                log_client, log_group_name, humio_log_ingester_arn, context
            )
