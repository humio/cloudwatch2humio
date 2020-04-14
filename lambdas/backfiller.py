import boto3
import json
import os
import helpers
from time import sleep

# Set environment variables.
humio_log_ingester_arn = os.environ["humio_log_ingester_arn"]
humio_subscription_prefix = os.environ.get("humio_subscription_prefix")

# Set up CloudWatch Logs client.
log_client = boto3.client("logs")


def lambda_handler(event, context):
    """
    Back-filler function that lists all log groups and subscribes to them.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda object context.
    :type context: obj

    :return: None
    :rtype: NoneType
    """
    # Grab all log groups with a token and/or prefix if we have them.
    if "nextToken" in event.keys():
        next_token = event["nextToken"]
        if humio_subscription_prefix:
            log_groups = log_client.describe_log_groups(
                logGroupNamePrefix=humio_subscription_prefix,
                nextToken=next_token
            )
        else:
            log_groups = log_client.describe_log_groups(
                nextToken=next_token
            )
    else:
        if humio_subscription_prefix:
            log_groups = log_client.describe_log_groups(
                logGroupNamePrefix=humio_subscription_prefix,
            )
        else:
            log_groups = log_client.describe_log_groups()

    # If we have a next token, recursively fire another instance of backfiller with it.
    # This is to look through all events.
    if "nextToken" in log_groups.keys():
        lambda_client = boto3.client("lambda")
        event["nextToken"] = log_groups["nextToken"]
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType="Event",
            Payload=json.dumps(event)
        )

    # Loop through log groups.
    for log_group in log_groups["logGroups"]:
        # Grab all subscriptions for the specified log group.
        all_subscription_filters = log_client.describe_subscription_filters(
            logGroupName=log_group["logGroupName"]
        )

        # First we check to see if there are any filters at all.
        if all_subscription_filters["subscriptionFilters"]:
            # If our function is not subscribed, delete subscription and create ours.
            if all_subscription_filters["subscriptionFilters"][0]["destinationArn"] != humio_log_ingester_arn:
                helpers.delete_subscription(
                    log_client,
                    log_group["logGroupName"],
                    all_subscription_filters["subscriptionFilters"][0]["filterName"]
                )
                helpers.create_subscription(
                    log_client,
                    log_group["logGroupName"],
                    humio_log_ingester_arn,
                    context
                )
            # We are now subscribed.
            else:
                print("We are already subscribed to %s" % log_group["logGroupName"])
        # When there are no subscription filters, let us subscribe!
        else:
            helpers.create_subscription(
                log_client,
                log_group["logGroupName"],
                humio_log_ingester_arn, context
            )

        # Keep hitting rate limits?
        # TODO: Find actual limits and back off using those.
        sleep(0.8)
