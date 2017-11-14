#!/bin/bash

set -e 

stack_name="humio-cloudwatch-suite"
humio_ingest_token=""
humio_dataspace_name="your-dataspace"
humio_auto_subscription="true"
humio_auto_backfiller="true"

check_install_status () {
    install_status=$(aws cloudformation list-stacks | jq --arg stack_name "$stack_name" -r '.StackSummaries[] | select(.StackName == $stack_name) | .StackStatus')
}

invoke_log_group_backfiller () {
   backfiller_resource_id=$(aws cloudformation describe-stack-resources --stack-name $stack_name  | jq -r '.StackResources[] | select(.LogicalResourceId == "HumioCloudwatchBackfiller") | .PhysicalResourceId')
   aws lambda invoke --function-name $backfiller_resource_id --payload "{}" --invocation-type Event -
}

#invoke_log_group_backfiller
if command -v aws>/dev/null 2>&1; then
    echo "found aws cli, installing humio ingestion suite..."

    # run the install using cloudformation
    aws cloudformation create-stack --stack-name $stack_name \
        --template-url https://s3.amazonaws.com/humio-public-us-east-1/cloudformation.json \
        --capabilities CAPABILITY_IAM \
        --parameters ParameterKey=HumioIngestToken,ParameterValue=$humio_ingest_token ParameterKey=HumioDataspaceName,ParameterValue=$humio_dataspace_name ParameterKey=HumioAutoSubscription,ParameterValue=$humio_auto_subscription ParameterKey=HumioSubscriptionBackfiller,ParameterValue=$humio_auto_backfiller > /dev/null 2>&1

    if [ "$humio_auto_subscription" == "true" ]; then
        # wait until the stack is installed
        until [ "$install_status" == "CREATE_COMPLETE" ]; do 
            check_install_status
            if [ "$install_status" == "ROLLBACK_COMPLETE" ]; then
                echo "Something went wrong, exiting..."
                echo "Please check the cloudformation panel in your AWS account for more information on what went wrong."
                exit 1
            fi
            echo -n "."
            sleep 1
        done
        echo ""
        echo "install complete! We will now connect all of your cloudformation log groups to the humio log ingester."   
        echo "triggering backfiller with an empty nextToken..."
        if invoke_log_group_backfiller; then
            invoke_log_group_backfiller
            echo "backfiller triggered! Your log groups should start shipping to humio shortly"
            exit 0
        else
            echo "Something went wrong..."
            exit 1
        fi 
    else
        echo "install complete! You can create a subscription to the humio lambda manually in your existing lambda triggers."
    fi
fi

