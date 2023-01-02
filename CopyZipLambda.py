# This file contains the inline code for the lambda named "LogScaleCloudWatchCopyZipLambda".
# This code is copied directly into the CF resource, and thus this file is only to have an overview.
# This code is based on the inline code from the following GitHub library https://github.com/aws-quickstart/quickstart-examples/blob/main/patterns/LambdaZips/example.yaml.

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


def copy_objects(source_bucket, dest_bucket, key):
    """
    Copy ZIP file from source bucket to destination bucket.

    :param source_bucket: S3 bucket containing ZIP file with code.
    :param dest_bucket: S3 bucket where ZIP file with code should be copied to.
    :param key: File name of the ZIP file with code.
    :return: None
    """
    s3 = boto3.client('s3')
    copy_source = {
        'Bucket': source_bucket,
        'Key': key
    }
    logger.debug(('copy_source: %s' % copy_source))
    logger.debug(('dest_bucket = %s' % dest_bucket))
    logger.debug(('key = %s' % key))
    s3.copy_object(CopySource=copy_source, Bucket=dest_bucket, Key=key)


def delete_objects(bucket, key):
    """
    Delete a bucket.

    :param bucket: S3 bucket to be deleted.
    :param key: S3 key to object that should be deleted.
    :return:
    """
    s3 = boto3.client('s3')
    s3.delete_objects(Bucket=bucket, Delete=key)


def timeout(event, context):
    """
    Send a response to the custom resource if it times out.

    :param event: Event data from the Lambda.
    :param context: Lambda context object.
    :return: None
    """
    logging.error('Execution is about to time out, sending failure response to CloudFormation')
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, None)


def handler(event, context):
    """
    Lambda handler that will copy the ZIP file from the source bucket to the
    destination bucket.

    It will send a failure to CloudFormation if the function is going to timeout.

    :param event: Event data from caller.
    :param context: Lambda context object.
    :return:  None
    """
    timer = threading.Timer((context.get_remaining_time_in_millis()
                             / 1000.00) - 0.5, timeout, args=[event, context])
    timer.start()
    logger.debug(('Received event: %s' % json.dumps(event)))
    status = cfnresponse.SUCCESS
    try:
        source_bucket = event['ResourceProperties']['SourceBucket']
        dest_bucket = event['ResourceProperties']['DestBucket']
        key = event['ResourceProperties']['Key']
        if event['RequestType'] == 'Delete':
            delete_objects(dest_bucket, key)
        else:
            copy_objects(source_bucket, dest_bucket, key)
    except Exception as e:
        logging.error('Exception: %s' % e, exc_info=True)
        status = cfnresponse.FAILED
    finally:
        timer.cancel()
        cfnresponse.send(event, context, status, {}, None)