import boto3
import json
import helpers
from datetime import datetime, timedelta, timezone
import os
import logging

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


def lambda_handler(event, context):
    """
    Ingest CloudWatch Metrics data to LogScale repository.

    :param event: Event data.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    helpers.setup()

    # Load user defined configurations for the API request. 
    configurations = json.load(open("conf_metric_ingester.json", "r"))

    # Set next token if one is present in the event.
    if "NextToken" in event.keys():
        configurations["NextToken"] = event["NextToken"]

    # Set default start time if none is present.
    if "StartTime" not in configurations.keys():
        if "StartTime" in event.keys():
            configurations["StartTime"] = event["StartTime"]
        else:
            configurations["StartTime"] = (datetime.utcnow() - timedelta(minutes=15))\
                .replace(tzinfo=timezone.utc).isoformat()  # 15 minutes ago.
    
    # Set default end time if none is present. 
    if "EndTime" not in configurations.keys():
        if "EndTime" in event.keys():
            configurations["EndTime"] = event["EndTime"]
        else:
            configurations["EndTime"] = datetime.utcnow()\
                .replace(tzinfo=timezone.utc).isoformat()  # Now.
            
    # Make CloudWatch:GetMetricData API request.
    metric_data = get_metric_data(configurations)

    # If there is a next token in the metric data,
    # then use this to retrieve the rest of the metrics recursively.
    if "NextToken" in metric_data:
        lambda_client = boto3.client("lambda")
        # Pass on next token, start time, and end time.
        event["NextToken"] = metric_data["NextToken"]
        event["StartTime"] = configurations["StartTime"]
        event["EndTime"] = configurations["EndTime"]
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType="Event",
            Payload=json.dumps(event)
        )

    # Format metric data to LogsScale event data.
    logscale_events = create_logscale_events(metric_data, configurations)

    # Send LogScale event data to LogScale.
    helpers.ingest_events(logscale_events, "cloudwatch_metrics")


def get_metric_data(configurations):
    """
    Make CloudWatch:GetMetricData API request.

    :param configurations: User defined API request parameters for the boto client.
    :type configurations: list

    :return: Metric data retrieved from request.
    :rtype: dict
    """
    # Create CloudWatch client.
    metric_client = boto3.client("cloudwatch")

    # Make GetMetricData API request.
    metric_data = metric_client.get_metric_data(
        **configurations
    )
    return metric_data


def create_logscale_events(metrics, configurations):
    """
    Create list of LogScale events based on metrics.

    :param metrics: Metrics received from GetMetricData.
    :type metrics: dict

    :param configurations: User defined API request parameters for the boto client.
    :type configurations: dict

    :return: Events to be sent to LogScale.
    :rtype: list
    """
    logscale_events = []

    # Create LogScale event based on each extracted timestamp.
    for result in metrics["MetricDataResults"]:
        count = 0
        for timestamp in result["Timestamps"]:
            timestamp = timestamp.replace(tzinfo=timezone.utc).isoformat()
            event = {
                "timestamp": timestamp,
                "attributes": {
                    "metricDataResults": {
                        "id": result["Id"],
                        "label": result["Label"],
                        "value": result["Values"][count],
                        "status_code": result["StatusCode"]
                    },
                    "messages": metrics.get("Messages", "None"),
                    "requestType": "GetMetricData",
                    "requestParameters": configurations
                }
            }
            logscale_events.append(event)
            count += 1

    return logscale_events
