import re
import json
import os
from botocore.vendored import requests  # TODO: Use the requests library.
import helpers

# False when setup has not been performed.
_is_setup = False

_is_setup = False

def setup():
    """
    Sets up variables that should persists across Lambda invocations.

    :return: None
    :rtype: NoneType
    """
    global humio_host
    global humio_protocol
    global humio_repository
    global humio_ingest_token
    global http_session

    humio_host = os.environ['humio_host']
    humio_protocol = os.environ['humio_protocol']
    humio_repository = os.environ['humio_repository_name']
    humio_ingest_token = os.environ['humio_ingest_token']

    http_session = requests.session()

    global _is_setup
    _is_setup = True


def lambda_handler(event, context):
    """
    Ingest CloudWatch Logs to Humio repository.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda object context.
    :type context: obj

    :return: None
    :rtype: NoneType
    """
    # TODO: Is there a better way?
    if not _is_setup:
        setup()

    # TODO: Use Python Client.
    humio_url = '%s://%s/api/v1/dataspaces/%s/ingest' % (humio_protocol, humio_host, humio_repository)
    humio_headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer %s' % humio_ingest_token
    }

    # Decode and unzip the log data.
    decoded_event = helpers.decode_event(event)

    # Debug output.
    print('Event from CloudWatch Logs: %s' % (json.dumps(decoded_event)))

    # Extract the general attributes from the event batch.
    batch_attrs = {
        'owner': decoded_event.get('owner', 'undefined'),
        'logGroup': decoded_event.get('logGroup', 'undefined'),
        'logStream': decoded_event.get('logStream', 'undefined'),
        'messageType': decoded_event.get('messageType', 'undefined'),
        'subscriptionFilters': decoded_event.get('subscriptionFilters', 'undefined')
    }

    # Parse out the service name.
    log_group_parser = re.compile('^/aws/(lambda|apigateway)/(.*)')
    parsed_log_group = log_group_parser.match(decoded_event.get('logGroup', ''))
    if parsed_log_group:
        batch_attrs.update(
            {
                'awsServiceName': parsed_log_group.group(1),
                'parsedLogGroupName': parsed_log_group.group(2)
            }
        )

    # Flatten the events from CloudWatch Logs.
    humio_events = []
    for log_event in decoded_event['logEvents']:
        message = log_event['message']

        # Create the attributes.
        attributes = {}
        attributes.update(batch_attrs)
        attributes.update(parse_message(message))

        # Append the flattened event
        humio_events.append({
            'timestamp': log_event['timestamp'],
            'rawstring': message,
            'kvparse': True,
            'attributes': attributes,
        })

    # Make a batch for the Humio Ingest API.
    wrapped_data = [{'tags': {'host': 'lambda'}, 'events': humio_events}]

    # Make request.
    request = http_session.post(
        humio_url,
        data=json.dumps(wrapped_data).encode(),  # encode might not be necessary.
        headers=humio_headers
    )

    response = request.text

    # Debug output.
    print('Got response %s from Humio.' % response)


# Standard out from Lambdas.
std_matcher = re.compile(
    '\d\d\d\d-\d\d-\d\d\S+\s+(?P<request_id>\S+)'
)


# END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile(
    'END RequestId:\s+(?P<request_id>\S+)'
)


# START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Version: $LATEST
start_matcher = re.compile(
    'START RequestId:\s+(?P<request_id>\S+)\s+'
    'Version: (?P<version>\S+)'
)


# REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
# Duration: 0.47 ms
# Billed Duration: 100 ms
# Memory Size: 128 MB
# Max Memory Used: 20 MB
report_matcher = re.compile(
    'REPORT RequestId:\s+(?P<request_id>\S+)\s+'
    'Duration: (?P<duration>\S+) ms\s+'
    'Billed Duration: (?P<billed_duration>\S+) ms\s+'
    'Memory Size: (?P<memory_size>\S+) MB\s+'
    'Max Memory Used: (?P<max_memory>\S+) MB'
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
    if message.startswith('END'):
        m = end_matcher.match(message)
    elif message.startswith('START'):
        m = start_matcher.match(message)
    elif message.startswith('REPORT'):
        m = report_matcher.match(message)
    else:
        m = std_matcher.match(message)

    if m:
        return m.groupdict()
    else:
        return {}
