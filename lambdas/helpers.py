import gzip
import json
import base64
import re


def decode_event(event):
    """
    Unzip and decode given event.

    :param event: CloudWatch Log event.
    :type event: obj

    :return: Unzipped and decoded event.6
    :rtype: JSON
    """
    decoded_json_event = gzip.decompress(base64.b64decode(event["awslogs"]["data"]))
    decoded_event = json.loads(decoded_json_event)
    return decoded_event


def create_subscription(log_client, log_group_name, humio_log_ingester_arn, context):
    """
    Create subscription to CloudWatch Logs specified log group.

    :param log_client: Boto client for CloudWatch Logs.

    :param log_group_name: Name of the log group.
    :type log_group_name: str

    :param humio_log_ingester_arn: Name of the Ingester resource.
    :type humio_log_ingester_arn: str

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # We cannot subscribe to the log group that our stdout/err goes to.
    if context.log_group_name == log_group_name:
        print("Skipping our own log group name...")
    else:
        print("Creating subscription for %s" % log_group_name)
    try:
        log_client.put_subscription_filter(
            logGroupName=log_group_name,
            filterName="%s-humio_ingester" % log_group_name,
            filterPattern="",  # Matching everything.
            destinationArn=humio_log_ingester_arn,
            distribution="ByLogStream"
        )
        print("Successfully subscribed to %s!" % log_group_name)
    except Exception as exception:
        print("Error creating subscription to %s. Exception: %s" % (log_group_name, exception))


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
    print("Deleting subscription for %s" % log_group_name)
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
    "\d\d\d\d-\d\d-\d\d\S+\s+(?P<request_id>\S+)"
)


# END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile(
    "END RequestId:\s+(?P<request_id>\S+)"
)


# START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Version: $LATEST
start_matcher = re.compile(
    "START RequestId:\s+(?P<request_id>\S+)\s+"
    "Version: (?P<version>\S+)"
)


# REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Duration: 0.47 ms
# Billed Duration: 100 ms
# Memory Size: 128 MB
# Max Memory Used: 20 MB
report_matcher = re.compile(
    "REPORT RequestId:\s+(?P<request_id>\S+)\s+"
    "Duration: (?P<duration>\S+) ms\s+"
    "Billed Duration: (?P<billed_duration>\S+) ms\s+"
    "Memory Size: (?P<memory_size>\S+) MB\s+"
    "Max Memory Used: (?P<max_memory>\S+) MB"
)
