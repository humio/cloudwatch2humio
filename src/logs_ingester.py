import re
import json
import helpers
import os
import logging

level = os.getenv("log_level", "INFO")
logger = logging.getLogger()
logging.basicConfig(level=level)

# False when setup has not been performed.
_is_setup = False

def lambda_handler(event, context):
    """
    Extract log data from CloudWatch Logs events and
    pass the data onto the Humio ingester.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # Persist variables across lambda invocations.
    if not _is_setup:
        helpers.setup()

    # Decode and unzip the log data.
    decoded_event = helpers.decode_event(event)

    # Debug output.
    logger.debug("Event from CloudWatch Logs: %s" % (json.dumps(decoded_event)))

    # Extract the general attributes from the event batch.
    batch_attrs = {
        "owner": decoded_event.get("owner", "undefined"),
        "logGroup": decoded_event.get("logGroup", "undefined"),
        "logStream": decoded_event.get("logStream", "undefined"),
        "messageType": decoded_event.get("messageType", "undefined"),
        "subscriptionFilters": decoded_event.get("subscriptionFilters", "undefined"),
    }

    # Parse out the service name.
    log_group_parser = re.compile("^/aws/(lambda|apigateway)/(.*)")
    parsed_log_group = log_group_parser.match(decoded_event.get("", ""))
    if parsed_log_group:
        batch_attrs.update(
            {
                "awsServiceName": parsed_log_group.group(1),
                "parsedLogGroupName": parsed_log_group.group(2)
            }
        )

    # Flatten the events from CloudWatch Logs.
    humio_events = []
    for log_event in decoded_event["logEvents"]:
        message = log_event["message"]

        # Create the attributes.
        attributes = {}
        attributes.update(batch_attrs)
        attributes.update(helpers.parse_message(message))

        # Append the flattened event
        humio_events.append({
            "timestamp": log_event["timestamp"],
            "rawstring": message,
            "kvparse": True,
            "attributes": attributes,
        })

    # Make request to Humio.
    request = helpers.ingest_events(humio_events, 'cloudwatch_logs')

    response = request.text

    # Debug output.
    logger.debug("Got response %s from Humio." % response)
