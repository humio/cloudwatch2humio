import boto3
import json
import helpers
from datetime import datetime, timedelta, timezone

_is_setup = False


def lambda_handler(event, context):
    """
    Ingest CloudWatch Metrics data to Humio repository.

    :param event: Event data.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # Persist variables across lambda invocations.
    if not _is_setup:
        helpers.setup()

    # Load user defined configurations for the API request. 
    user_defined_data = json.load(open("user_defined_metric_data.json", "r"))

    # Set next token if one is present in the event.
    if "NextToken" in event.keys():
        user_defined_data["NextToken"] = event["NextToken"]

    # Set default start time if none is present.
    if "StartTime" not in user_defined_data.keys():
        if "StartTime" in event.keys():
            user_defined_data["StartTime"] = event["StartTime"]
        else:
            user_defined_data["StartTime"] = (datetime.utcnow() - timedelta(minutes=15))\
                .replace(tzinfo=timezone.utc).isoformat()  # 15 minutes ago.
    
    # Set default end time if none is present. 
    if "EndTime" not in user_defined_data.keys():
        if "EndTime" in event.keys():
            user_defined_data["EndTime"] = event["EndTime"]
        else:
            user_defined_data["EndTime"] = datetime.utcnow()\
                .replace(tzinfo=timezone.utc).isoformat()  # Now.
            
    # Make CloudWatch:GetMetricData API request.
    metric_data = get_metric_data(user_defined_data)

    # If there is a next token in the metric data,
    # then use this to retrieve the rest of the metrics recursively.
    if "NextToken" in metric_data:
        lambda_client = boto3.client("lambda")
        # Pass on next token, start time, and end time.
        event["NextToken"] = metric_data["NextToken"]
        event["StartTime"] = user_defined_data["StartTime"]
        event["EndTime"] = user_defined_data["EndTime"]
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType="Event",
            Payload=json.dumps(event)
        )

    # Format metric data to Humio event data.
    humio_events = create_humio_events(metric_data, user_defined_data)

    # Send Humio event data to Humio.
    request = helpers.ingest_events(humio_events, "cloudwatch_metrics")

    # Debug the response.
    response = request.text
    print("Got response %s from Humio." % response)


def get_metric_data(user_defined_data):
    """
    Make CloudWatch:GetMetricData API request.

    :param user_defined_data: User defined API request parameters for the boto client.
    :type user_defined_data: list

    :return: Metric data retrieved from request.
    :rtype: dict
    """
    # Create CloudWatch client.
    metric_client = boto3.client("cloudwatch")

    # Make GetMetricData API request.
    metric_data = metric_client.get_metric_data(
        **user_defined_data
    )
    return metric_data


def create_humio_events(metrics, user_defined_data):
    """
    Create list of Humio events based on metrics.

    :param metrics: Metrics received from GetMetricData.
    :type metrics: dict

    :param user_defined_data: User defined API request parameters for the boto client.
    :type user_defined_data: dict

    :return: Events to be sent to Humio.
    :rtype: list
    """
    humio_events = []

    # Create Humio event based on each extracted timestamp. 
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
                    "userDefinedData": user_defined_data
                }
            }
            humio_events.append(event)
            count += 1

    return humio_events
