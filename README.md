# cloudwatch2humio

This Humio integration will connect your AWS Cloudwatch Log Groups to an AWS Lambda that ships your logs from Cloudwatch Logs to Humio. Below you'll find installation and troubleshooting steps. If you have any issues, please join us on slack at [meethumio.slack.com](https://meethumio.slack.com). 

## Installation

You can install the cloudwatch2humio integration using the installation script or the cloudformation directly using the cloudformation template buttons per region:

**US East 1**:
[![Install cloudwatch2humio in US East 1](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png "Install cloudwatch2humio in US East 1")](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=cloudwatch2humio&templateURL=https://s3.amazonaws.com/humio-public-us-east-1/cloudformation.json)

**EU Central 1**:
[![Install cloudwatch2humio in EU Central 1](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png "Install cloudwatch2humio in EU Central 1")](https://console.aws.amazon.com/cloudformation/home?region=eu-central-1#/stacks/new?stackName=cloudwatch2humio&templateURL=https://s3.amazonaws.com/humio-public-us-east-1/cloudformation.json)

### Cloudformation

The humio ingestion suite uses Cloudformation to install itself.

The cloudformation template supports the following parameters:

* `HumioDataspaceName` - The name of your dataspace in humio that you want to ship logs to.
* `HumioProtocol` - The transport protocol used for delivering log events to Humio. HTTPS is default and recommended.
* `HumioHost` - The host you want to ship your humio logs to. 
* `HumioIngestToken` - The value of your ingest token from your Humio account.
* `HumioSubscriptionPrefix` - By adding this filter the Humio Ingester will only subscribe to log groups that start with this prefix.
* `HumioSubscriptionBackfiller` - This will check for missed or old log groups that existed before the Humio integration will install. This increases execution time of the lambda by about 1s. By default this is **true**.

Once you know the parameters you want to customize, you can apply the template by running the following command:

```
$ aws cloudformation create-stack --stack-name humio-test --template-url https://humio-public-us-east-1.s3.amazonaws.com/cloudformation.json --capabilities CAPABILITY_IAM --parameters ParameterKey=HumioIngestToken,ParameterValue=asdf ParameterKey=HumioDataspaceName,ParameterValue=humio-test
{
    "StackId": "arn:aws:cloudformation:us-east-1:319725471239:stack/humio-test/4b7ffbf0-8ed0-11e7-ab8c-500c285eae99"
}
```

You can use the following command to check up on the status of your stack create:

```
$ aws cloudformation list-stacks
{
    "StackSummaries": [
        {
            "StackId": "arn:aws:cloudformation:us-east-1:319725471239:stack/humio-test/4b7ffbf0-8ed0-11e7-ab8c-500c285eae99",
            "StackName": "humio-test",
            "CreationTime": "2017-09-01T04:44:53.274Z",
            "StackStatus": "CREATE_COMPLETE"
        }
    ]
}
```

## How this integration works

This integration will install three lambas, the `AutoSubscriber`,`CloudwatchIngester` and the `CloudwatchBackfiller`.

### Ingester

This function handles the delivery of your Cloudwatch log events to Humio.

### Auto Subscriber
This function will auto subscribe the Humio Log Ingester every time a new log group is created. This is done by filtering CloudTrail events and triggering the auto subscription lambda every time a new log group is created.

### Backfiller
This will run if you have set `humio_auto_backfiller` to `true` in the `install.sh` script or have set `HumioSubscriptionBackfiller` when executing the CloudFormation template. This function will paginate through your existing cloudwatch log groups and subscribe the Humio Log Ingester to every single one.

