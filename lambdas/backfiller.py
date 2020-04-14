import boto3
import gzip
import json
import os
import helpers
from time import sleep

# setup log client
log_client = boto3.client("logs")

# env vars
humio_log_ingester_arn = os.environ["humio_log_ingester_arn"]
humio_subscription_prefix = os.environ.get("humio_subscription_prefix")

# long running function that lists all log groups and subscribes to them
def lambda_handler(event, context):

    # grab all log groups with a token if we have it
    if "nextToken" in event.keys():
        nextToken = event["nextToken"]
        if humio_subscription_prefix:
            log_groups = log_client.describe_log_groups(
                logGroupNamePrefix=humio_subscription_prefix, nextToken=nextToken
            )
        else:
            log_groups = log_client.describe_log_groups(nextToken=nextToken)
    else:
        if humio_subscription_prefix:
            log_groups = log_client.describe_log_groups(
                logGroupNamePrefix=humio_subscription_prefix
            )
        else:
            log_groups = log_client.describe_log_groups()

    # if we have a token, recursively fire another instance of backfiller with it
    if "nextToken" in log_groups.keys():
        lambda_cli = boto3.client("lambda")
        event["nextToken"] = log_groups["nextToken"]
        lambda_cli.invoke_async(
            FunctionName=context.function_name, InvokeArgs=json.dumps(event)
        )

    # loop through log groups
    for logGroup in log_groups["logGroups"]:

        # grab all subscriptions for the specified log group
        all_subscription_filters = log_client.describe_subscription_filters(
            logGroupName=logGroup["logGroupName"]
        )

        # first we check to see if there are any filters at all
        if all_subscription_filters["subscriptionFilters"]:

            # if our function is not subscribed delete subscription and create ours
            if (
                all_subscription_filters["subscriptionFilters"][0]["destinationArn"]
                != humio_log_ingester_arn
            ):
                helpers.delete_subscription(
                    log_client,
                    logGroup["logGroupName"],
                    all_subscription_filters["subscriptionFilters"][0]["filterName"],
                )
                helpers.create_subscription(
                    log_client,
                    logGroup["logGroupName"],
                    humio_log_ingester_arn,
                    context,
                )

            # we are subbed
            else:
                print("We are subscribed to %s" % logGroup["logGroupName"])

        # there are no filters, lets subscribe!
        else:
            helpers.create_subscription(
                log_client, logGroup["logGroupName"], humio_log_ingester_arn, context
            )

        # keep hitting rate limits? TODO: find actual limits and back off using those
        sleep(0.8)
