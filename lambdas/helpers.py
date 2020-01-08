def create_subscription(log_client, log_group_name, humio_log_ingester_arn, context):
    
    # can't subscribe to the log group that our stdout/err goes to
    if context.log_group_name == log_group_name:
        print("Skipping our own log group name...")
    else:
        print("Creating subscription for %s" % log_group_name)
	try:
            response = log_client.put_subscription_filter(
                logGroupName=log_group_name,
                filterName="%s-humio_ingester" % log_group_name,
                filterPattern='',
                destinationArn=humio_log_ingester_arn,
                distribution='ByLogStream'
            )
            print('subscribed to %s!' % log_group_name)
	except Exception as e:
	    print('Error creating subscription to %s. Exception: %s' % (log_group_name, e))

def delete_subscription(log_client, logGroupName, filterName):
    print("Deleting subscription for %s" % logGroupName)
    response = log_client.delete_subscription_filter(
        logGroupName=logGroupName,
        filterName=filterName
    )
