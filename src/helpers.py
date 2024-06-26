import gzip
import base64
import re
import os
import json
import requests
import logging

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)

_is_setup = False


def setup():
    """
    Sets up variables that should persists across Lambda invocations.

    This can be called every invocation but we will only run it once
    per Lambda instance.
    """
    global logscale_host
    global logscale_protocol
    global logscale_ingest_token
    global http_session
    global _is_setup

    if _is_setup:
        return

    logscale_host = os.environ["logscale_host"]
    logscale_protocol = os.environ["logscale_protocol"]
    logscale_ingest_token = os.environ["logscale_ingest_token"]
    http_session = requests.Session()

    _is_setup = True


def ingest_events(logscale_events, host_type):
    """
    Wrap and send CloudWatch Logs/Metrics to LogScale repository.

    :param logscale_events: Structured events to be ingested into LogScale.
    :type logscale_events: list

    :param host_type: Type of host from which the events are being sent.
    :type host_type: str

    :return: Response object from request.
    :rtype: obj
    """
    logscale_url = "%s://%s/api/v1/ingest/humio-structured" % (logscale_protocol, logscale_host)
    logscale_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % logscale_ingest_token
    }

    # Prepare events to be sent to LogScale.
    wrapped_data = [{"tags": {"host": host_type}, "events": logscale_events}]

    logger.debug("Data being sent to LogScale: %s" % wrapped_data)

    # Make request. 
    response = http_session.post(
        logscale_url,
        data=json.dumps(wrapped_data),
        headers=logscale_headers
    )
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Got error %s from LogScale." % response.text, exc_info= e)
    else:
        logger.debug("Got response %s from LogScale." % response.text)

    return response


def decode_event(event):
    """
    Unzip and decode given event.

    :param event: CloudWatch Log event.
    :type event: dict

    :return: Unzipped and decoded event.
    :rtype: dict
    """
    decoded_json_event = gzip.decompress(base64.b64decode(event["awslogs"]["data"]))
    decoded_event = json.loads(decoded_json_event)

    return decoded_event


def create_subscription(log_client, log_group_name, logscale_log_ingester_arn, context):
    """
    Create subscription to CloudWatch Logs specified log group.

    :param log_client: Boto client for CloudWatch Logs.
    :type log_client: obj

    :param log_group_name: Name of the log group.
    :type log_group_name: str

    :param logscale_log_ingester_arn: Name of the logs ingester resource.
    :type logscale_log_ingester_arn: str

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """   
    # We cannot subscribe to the log group that our stdout/err goes to.
    if context.log_group_name == log_group_name:
        logger.debug("Skipping our own log group name...")
    # And we do not want to subscribe to other LogScale log ingesters - if there are any.
    if "HumioCloudWatchLogsIngester" in log_group_name:
        logger.debug("Skipping cloudwatch2logscale ingesters...")
    # And we do not want to subscribe to other LogScale log ingesters - if there are any.
    if "LogScaleCloudWatchLogsIngester" in log_group_name:
        logger.debug("Skipping cloudwatch2logscale ingesters...")
    else:
        logger.info("Creating subscription for %s" % log_group_name)
        try:
            log_client.put_subscription_filter(
                logGroupName=log_group_name,
                filterName="%s-logscale_ingester" % log_group_name,
                filterPattern="",  # Matching everything.
                destinationArn=logscale_log_ingester_arn,
                distribution="ByLogStream"
            )
            logger.debug("Successfully subscribed to %s!" % log_group_name)
        except Exception as exception:
            logger.error("Error creating subscription to %s. Exception: %s" % (log_group_name, exception))


def delete_subscription(log_client, log_group_name, filter_name):
    """
    Delete subscription to CloudWatch Logs specified log group.

    :param log_client: Boto client for CloudWatch Logs.
    :param log_client: obj

    :param log_group_name: Name of the log group.
    :type log_group_name: str

    :param filter_name: Name of the subscription filter.
    :type filter_name: str

    :return: None
    """    
    logger.info("Deleting subscription for %s" % log_group_name)
    log_client.delete_subscription_filter(
        logGroupName=log_group_name,
        filterName=filter_name
    )


def parse_message(message):
    """
    Simple CloudWatch Logs parser.

    :param message: Log event message.
    :type message: str

    :return: Parsed message or empty.
    :rtype: dict
    """
    m = None

    # Determine which matcher to use depending on the message type.
    if message.startswith("END"):
        m = end_matcher.match(message)
    elif message.startswith("START"):
        m = start_matcher.match(message)
    elif message.startswith("REPORT"):
        m = report_matcher.match(message)
    else:
        m = std_matcher.match(message)

    if m:
        return m.groupdict()
    else:
        return {}


# Standard out from Lambdas.
std_matcher = re.compile(
    r"\d\d\d\d-\d\d-\d\d\S+\s+(?P<request_id>\S+)"
)


# END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile(
    r"END RequestId:\s+(?P<request_id>\S+)"
)


# START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Version: $LATEST
start_matcher = re.compile(
    r"START RequestId:\s+(?P<request_id>\S+)\s+"
    r"Version: (?P<version>\S+)"
)


# REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Duration: 0.47 ms
# Billed Duration: 100 ms
# Memory Size: 128 MB
# Max Memory Used: 20 MB
report_matcher = re.compile(
    r"REPORT RequestId:\s+(?P<request_id>\S+)\s+"
    r"Duration: (?P<duration>\S+) ms\s+"
    r"Billed Duration: (?P<billed_duration>\S+) ms\s+"
    r"Memory Size: (?P<memory_size>\S+) MB\s+"
    r"Max Memory Used: (?P<max_memory>\S+) MB"
)
