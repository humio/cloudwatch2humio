
# CloudWatch2Humio

This repository contains a set of lambdas for shipping Cloudwatch Logs and Metrics
to Humio.

For making a quick launch see the documentation:

https://docs.humio.com/integrations/platform-integrations/aws-cloudwatch/

For a manual set up, follow along with this guide! 

## Manual Setup

This integration uses CloudFormation to set up a set of lambda functions which can retrieve logs and metrics from CloudWatch. 

### Prerequisites

* AWS CLI installed and setup with an AWS account allowed to create a CloudFormation stack. 

### Setup

#### 1. Create a zip file with the content of the **src** folder

On linux:

> $ make

On windows:

1. Create a folder named **target** in root, and copy all files from **src** into it.
2. Install requirements into the **target** folder using pip:

    > pip3 install -r requirements.txt -t target

3. In the **target** folder, zip all files into **cloudwatch_humio.zip**. 

#### 2. Create an AWS S3 bucket

The name of the AWS S3 bucket must be the same as the one specified in the CloudFormation file, beware of this if you choose another name.

> $ aws s3api create-bucket --bucket humio-public-REGION --create-bucket-configuration LocationConstraint=REGION

#### 3. Upload zip file to AWS S3 bucket. 

> $ aws s3 cp target/cloudwatch_humio.zip s3://humio-public-REGION/

#### 4. Create JSON file and define paramters.

Create a **parameters.json** file in the root folder, and at least specify the following parameters:

> {
>   "ParameterName": "HumioIngestToken",
>   "ParameterValue": "YOUR-SECRET-INGEST-TOKEN"
> }

Look in the CloudFormation file to see the other parameters available. 

#### 5. Create stack.

To create the stack using the CloudFormation file and the parameters that you have defined run:

> $ aws cloudformation create-stack --stack-name STACK-NAME --template-body file://cloudformation.json --parameters file://parameters.json --capabilities CAPABILITY_IAM --debug --region REGION

#### 6. (Optional) Delete stack.

If you want to delete the stack, then run the following command: 

> $ aws cloudformation delete-stack --stack-name STACK-NAME


