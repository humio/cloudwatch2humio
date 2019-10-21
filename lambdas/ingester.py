from __future__ import print_function

import re
import json
import os
import time
import calendar
import urllib.request as urlRequest
import urllib.parse as parse
import datetime
import base64
import gzip
import boto3
from time import sleep

from StringIO import StringIO
from datetime import tzinfo


################################################################################
### The main handler ###########################################################
################################################################################

def lambda_handler(event, context):
   
    ################################################################################
    ### Parameters for the lambda ##################################################
    ################################################################################

    humio_host = os.environ['humio_host']
    humio_protocol = os.environ['humio_protocol']
    humio_dataspace = os.environ['humio_dataspace_name']
    humio_ingest_token = os.environ['humio_ingest_token']

    ################################################################################
    ### Global variables ###########################################################
    ################################################################################

    humio_url = '%s://%s/api/v1/dataspaces/%s/ingest' % (humio_protocol, humio_host, humio_dataspace)
    humio_headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer %s' % humio_ingest_token
    }

    # decode and unzip the log data
    decoded_json_event = gzip.decompress(base64.b64decode(event['awslogs']['data']))
    decoded_event = json.loads(decoded_json_event)

    # debug output
    print(f"Event from Cloudwatch: {decoded_event}")


    # Extract general attributes from the event batch
    batch_attrs = {
        'owner': decoded_event.get('owner', 'undefined'),
        'logGroup': decoded_event.get('logGroup', 'undefined'),
        'logStream': decoded_event.get('logStream', 'undefined'),
        'messageType': decoded_event.get('messageType', 'undefined'),
        'subscriptionFilters': decoded_event.get('subscriptionFilters', 'undefined')
    }

    # parse out the service name 
    logGroupParser = re.compile('^/aws/(lambda|apigateway)/(.*)')
 
    parsedLogGroup = logGroupParser.match(decoded_event.get('logGroup', ""))
    if parsedLogGroup:
        batch_attrs.update(
            {
                'awsServiceName': parsedLogGroup.group(1),
                'parsedLogGroupName': parsedLogGroup.group(2)
            })

    # flatten the events from cloudwatch
    humio_events = []
    for logEvent in decoded_event['logEvents']:
        message = logEvent['message']

        # Create the attributes
        attributes={}
        attributes.update(batch_attrs)
        attributes.update(parse_message(message))

        # Append the flattened event
        humio_events.append({
            'timestamp': logEvent['timestamp'],
            'rawstring': message,
            'kvparse': True,
            'attributes': attributes,
        })

    # Make a batch for the Humio ingest API
    wrapped_data = [{ 'tags': {'host':'lambda'}, 'events': humio_events }]
    wrapped_data=json.dumps(wrapped_data)
    request_data=wrapped_data.encode()

    # prepare request
    request = urlRequest.Request(humio_url, request_data, humio_headers)

    # ship request
    f = urlRequest.urlopen(request)

    # read response
    response = f.read()

    # close handler
    # QUESTION: can we reuse this handler between lambda invocations?
    f.close()

    # debug output
    print('got response %s from humio' % response)

################################################################################
### Simple Cloudwatch parser ###################################################
################################################################################

#Standard out from lambdas
std_matcher = re.compile('\d\d\d\d-\d\d-\d\d\S+\s+(?P<request_id>\S+)')

#END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
end_matcher = re.compile('END RequestId:\s+(?P<request_id>\S+)')

#START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46 Version: $LATEST
start_matcher = re.compile('START RequestId:\s+(?P<request_id>\S+)\s+Version: (?P<version>\S+)')

#REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46	Duration: 0.47 ms	Billed Duration: 100 ms Memory Size: 128 MB	Max Memory Used: 20 MB
report_matcher = re.compile('REPORT RequestId:\s+(?P<request_id>\S+)\s+Duration: (?P<duration>\S+) ms\s+Billed Duration: (?P<billed_duration>\S+) ms\s+Memory Size: (?P<memory_size>\S+) MB\s+Max Memory Used: (?P<max_memory>\S+) MB')

def parse_message(message):
    m = None

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

### Some manual cli-testing of the parse_message function
#
#def p(s):
#    print (s)
#
#p(parse_message("2017-08-28T09:49:48.176Z 3aaf5224-8bd6-11e7-bb30-4f271af95c46 { message: 'humming right along {O,o} ' }"))
#p(parse_message("END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46"))
#p(parse_message("START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46 Version: $LATEST"))
#p(parse_message("REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46	Duration: 0.47 ms Billed Duration: 100 ms Memory Size: 128 MB Max Memory Used: 20 MB"))

# This is a seperate handler and not called at all through the normal ingestion execution flow
# update subscriptions before our next run


