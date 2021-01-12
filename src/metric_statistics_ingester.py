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
    Ingest CloudWatch Metric statistics to Humio repository.

    :param event: Event data.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    helpers.setup()

    # Load user defined configurations for the API request. 
    configurations = json.load(open("conf_metric_statistics_ingester.json", "r"))

    # Make CloudWatch:GetMetricStatistics API request.
    metric_statistics, api_parameters = get_metric_statistics(configurations)

    # Used for debugging.
    logger.debug("Statistics from CloudWatch Metrics: %s" % metric_statistics)

    # Format metric data to Humio event data.
    humio_events = create_humio_events(metric_statistics, api_parameters)

    # Send Humio event data to Humio.
    request = helpers.ingest_events(humio_events, "cloudwatch_metrics")

    # Debug the response.
    response = request.text
    logger.debug("Got response %s from Humio." % response)


def get_metric_statistics(configurations):
    """
    Make CloudWatch:GetMetricStatistics API request.

    :param configurations: User defined API request parameters for the boto client.
    This is a list of one or more API parameters to make one or more calls.
    :type configurations: list

    :return: Metric statistics retrieved from a request and the corresponding API parameters.
    :rtype: dict, dict
    """
    # Create CloudWatch client.
    metric_client = boto3.client("cloudwatch")

    # Make CloudWatch:GetMetricStatistics API request.
    for api_parameters in configurations:

        # Check whether start and end time has been set or defaults are to be used.
        if "StartTime" not in api_parameters.keys():
            api_parameters["StartTime"] = datetime.utcnow() - timedelta(minutes=15)  # 15 minutes ago.
            api_parameters["StartTime"] = api_parameters["StartTime"].replace(tzinfo=timezone.utc).isoformat()

        if "EndTime" not in api_parameters.keys():
            api_parameters["EndTime"] = datetime.utcnow()  # Now.
            api_parameters["EndTime"] = api_parameters["EndTime"].replace(tzinfo=timezone.utc).isoformat()

        # Used for debugging.
        logger.debug("Start time: %s, End time: %s" % (api_parameters["StartTime"], api_parameters["EndTime"]))

        # Make GetMetricStatistics API request.
        metric_statistics = metric_client.get_metric_statistics(
            **api_parameters
        )
        return metric_statistics, api_parameters


def create_humio_events(metrics, api_parameters):
    """
    Create list of Humio events based on metrics.

    :param metrics: Metrics received from GetMetricStatistics.
    :type metrics: dict

    :param lambda_event: API parameters used for the API request 
    to retrieve the metric statistics.
    :type lambda_event: dict

    :return: List of events to be sent to Humio.
    :rtype: list
    """
    humio_events = []

    # Used for debuggin.
    logger.debug("Datapoints: %s" % metrics["Datapoints"])

    # Create one Humio event per datapoint/timestamp.
    for datapoint in metrics["Datapoints"]:
        # Create event data.
        event = {
            "timestamp": datapoint["Timestamp"].replace(tzinfo=timezone.utc).isoformat(),
            "attributes": {
                "label": metrics["Label"],
                "datapoint": {
                    "sampleCount": datapoint.get("Samplecount", "None"),
                    "average": datapoint.get("Average", "None"),
                    "sum": datapoint.get("Sum", "None"),
                    "minimum": datapoint.get("Minimum", "None"),
                    "maximum": datapoint.get("Maximum", "None"),
                    "unit": datapoint["Unit"],
                    "extendedStatistics": datapoint.get("ExtendedStatistics", "None"),
                    "responseMetaData": metrics["ResponseMetadata"]
                },
                "requestType": "GetMetricStatistics",
                "requestParameters ": api_parameters
            }
        }
        humio_events.append(event)

    return humio_events
