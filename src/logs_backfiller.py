import boto3
import json
import os
import helpers
import requests
import logging

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


def lambda_handler(event, context):
    """
    Back-filler function that lists all log groups and subscribes to them.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # Create a reponse to the custom resource from the CF to make it finish.
    # This is used when starting the backfiller automatically.
    send_custom_resource_response(event, context)

    # Set environment variables.
    logscale_log_ingester_arn = os.environ["logscale_log_ingester_arn"]
    logscale_subscription_prefix = os.environ.get("logscale_subscription_prefix")

    # Set up CloudWatch Logs client.
    log_client = boto3.client("logs")

    # Grab all log groups with a token and/or prefix if we have them.
    if "nextToken" in event.keys():
        next_token = event["nextToken"]
        if logscale_subscription_prefix:
            log_groups = log_client.describe_log_groups(
                logGroupNamePrefix=logscale_subscription_prefix,
                nextToken=next_token
            )
        else:
            log_groups = log_client.describe_log_groups(
                nextToken=next_token
            )
    else:
        if logscale_subscription_prefix:
            log_groups = log_client.describe_log_groups(
                logGroupNamePrefix=logscale_subscription_prefix,
            )
        else:
            log_groups = log_client.describe_log_groups()

    # If we have a next token, recursively fire another instance of backfiller with it.
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
            if all_subscription_filters["subscriptionFilters"][0]["destinationArn"] != logscale_log_ingester_arn:
                # TODO: Do not delete subscriptions! It is better that it fails in this case instead of potentially ruining infrastructure.
                helpers.delete_subscription(
                    log_client,
                    log_group["logGroupName"],
                    all_subscription_filters["subscriptionFilters"][0]["filterName"]
                )
                helpers.create_subscription(
                    log_client,
                    log_group["logGroupName"],
                    logscale_log_ingester_arn,
                    context
                )
            # We are now subscribed.
            else:
                logger.debug("We are already subscribed to %s" % log_group["logGroupName"])
        # When there are no subscription filters, let us subscribe!
        else:
            helpers.create_subscription(
                log_client,
                log_group["logGroupName"],
                logscale_log_ingester_arn, context
            )


def send_custom_resource_response(event, context):
    if "LogicalResourceId" in event.keys():
        if event["LogicalResourceId"] == "LogScaleBackfillerAutoRunner":
            response_content = {
                "Status" : "SUCCESS",
                "RequestId" : event["RequestId"],
                "LogicalResourceId" : event["LogicalResourceId"],
                "StackId" : event["StackId"],
                "PhysicalResourceId" : event["ResourceProperties"]["StackName"] + "-LogScaleBackfillerAutoRunner"
            }
            response = requests.put(
                event["ResponseURL"],
                data=json.dumps(response_content)
            )
            # Used for debugging. 
            logger.debug("Response status from Custom Resource: %s " % response.status_code)
