import json
import os
import time
import base64
import gzip
import boto3
import StringIO
import urllib2

def humio_ingest(decoded_event):
    humio_host = os.environ['humio_host']
    humio_protocol = os.environ['humio_protocol']
    humio_dataspace = os.environ['humio_dataspace_name']
    humio_ingest_token = os.environ['humio_ingest_token']

    humio_url = '%s://%s/api/v1/dataspaces/%s/ingest' % (humio_protocol, humio_host, humio_dataspace)
    humio_headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer %s' % humio_ingest_token
    }
    
    # flatten the events from cloudwatch
    humio_events = []

    for record in decoded_event['Records']:
        
        # Append the flattened event
        humio_events.append({
            'timestamp': record['eventTime'],
            'attributes': record
        })

    # Make a batch for the Humio ingest API
    wrapped_data = [{ 'tags': {'service':'cloudtrail'}, 'events': humio_events }]
    
    # prepare request
    request = urllib2.Request(humio_url, json.dumps(wrapped_data), humio_headers)
    
    # ship request
    f = urllib2.urlopen(request)

    # read response
    response = f.read()

    # close handler
    f.close()

    # debug output
    print('got response %s from humio' % response)


def lambda_handler(event, context):

    s3 = boto3.resource('s3')
    
    for record in event['Records']: 
      bucket = s3.Bucket(record['s3']['bucket']['name'])
      try:
          bucket.download_file(record['s3']['object']['key'], '/tmp/cloudtrail.txt')
          with gzip.open('/tmp/cloudtrail.txt', 'r') as data:
            decoded_json_event = data.read()
            decoded_event = json.loads(decoded_json_event)
            humio_ingest(decoded_event)
            os.remove('/tmp/cloudtrail.txt')

      except Exception as e:
          raise
