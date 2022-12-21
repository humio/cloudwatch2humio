# This file contains the inline code for the lambda named "HumioCloudWatchCopyZipLambda".

import json
import logging
import os
import threading
import boto3
import cfnresponse

level = os.getenv("log_level", "INFO")
logging.basicConfig(level=level)
logger = logging.getLogger()
logger.setLevel(level)


def copy_objects(source_bucket, dest_bucket, prefix):
    s3 = boto3.client('s3')
    key = prefix
    copy_source = {
        'Bucket': source_bucket,
        'Key': key
    }
    logger.debug(('copy_source: %s' % copy_source))
    logger.debug(('dest_bucket = %s'%dest_bucket))
    logger.debug(('key = %s' %key))
    s3.copy_object(CopySource=copy_source, Bucket=dest_bucket, Key=key)


def delete_objects(bucket, prefix):
    s3 = boto3.client('s3')
    s3.delete_objects(Bucket=bucket, Delete=prefix)


def timeout(event, context):
    logging.error('Execution is about to time out, sending failure response to CloudFormation')
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)


def handler(event, context):
    # make sure we send a failure to CloudFormation if the function
    # is going to timeout
    timer = threading.Timer((context.get_remaining_time_in_millis()
                             / 1000.00) - 0.5, timeout, args=[event, context])
    timer.start()
    logger.debug(('Received event: %s' % json.dumps(event)))
    status = cfnresponse.SUCCESS
    try:
        source_bucket = event['ResourceProperties']['SourceBucket']
        dest_bucket = event['ResourceProperties']['DestBucket']
        prefix = event['ResourceProperties']['Prefix']
        if event['RequestType'] == 'Delete':
            delete_objects(dest_bucket, prefix)
        else:
            copy_objects(source_bucket, dest_bucket, prefix)
    except Exception as e:
        logging.error('Exception: %s' % e, exc_info=True)
        status = cfnresponse.FAILED
    finally:
        timer.cancel()
        cfnresponse.send(event, context, status, {}, None)