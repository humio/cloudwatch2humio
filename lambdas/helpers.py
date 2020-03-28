import gzip
import json
from StringIO import StringIO


def decode_event(event):
    """
    Unzip and decode given event.

    :param event: CloudWatch Log event.
    :type event: obj

    :return: Unzipped and decoded event.
    :rtype: JSON
    """
    decoded_json_event = gzip.GzipFile(
        fileobj=StringIO(
            event['awslogs']['data'].decode('base64', 'strict')
        )
    ).read()
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
            filterPattern='',
            destinationArn=humio_log_ingester_arn,
            distribution='ByLogStream'
        )
        print('Successfully subscribed to %s!' % log_group_name)
    except Exception as e:
        print('Error creating subscription to %s. Exception: %s' % (log_group_name, e))


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

