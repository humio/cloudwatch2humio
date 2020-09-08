# Contributing
Contributions are welcome, and they are greatly appreciated! 
Every little bit helps, and credit will always be given.

## Ways to Contribute
There are many different ways, in which you may contribute to this project, including:

   * Opening issues by using the [issue tracker](https://link-to-issue-tracker.com), using the correct issue template for your submission.
   * Commenting and expanding on open issues.
   * Propose fixes to open issues via a pull request.

We suggest that you create an issue on GitHub before starting to work on a pull request, as this gives us a better overview, and allows us to start a conversation about the issue.
We also encourage you to separate unrelated contributions into different pull requests. This makes it easier for us to understand your individual contributions and faster at reviewing them.

## Setting Up the Integration for Local Development
Following is described how to set up the integration for local development. 

### Prerequisites

* AWS CLI installed and setup with an AWS account allowed to create a CloudFormation stack. 
* Python 3x installed.

### Setup

1. Clone the git repository: https://github.com/humio/cloudwatch2humio 

2. In the project folder, create a zip file with the content of the *src* folder from the repository.
    - On Linux/MacOS: 
      
      This is done by using the present makefile: 
      
      ```
      $ make
      ```

    - On Windows:

      1. Create a folder named *target* in the project root folder, and copy all files from *src* into it.

      2. Install requirements into the *target* folder using pip: 

            ```
            pip3 install -r requirements.txt -t target
            ```

      3. In the *target* folder, zip all files into *YOUR-ZIP-NAME.zip*. 

3. Create an AWS S3 bucket using the following command: 

    ```
    aws s3api create-bucket --bucket YOUR-HUMIO-BUCKET --create-bucket-configuration LocationConstraint=YOUR-REGION
    ```

    - The name of the AWS S3 bucket must be the same as the one specified in the CloudFormation file.

4. Upload the zip file to the AWS S3 bucket: 

    ```
    aws s3 cp target/YOUR-ZIP-NAME.zip s3://YOUR-HUMIO-BUCKET/
    ``` 

5. Create a *parameters.json* file in the project root folder, and specify the CloudFormation parameters, for example: 

    ```
    [
        { 
            "ParameterKey": "HumioHost", 
            "ParameterValue": "cloud.humio.com" 
        },
        { 
            "ParameterKey": "HumioProtocol", 
            "ParameterValue": "https" 
        },
        { 
            "ParameterKey": "HumioIngestToken", 
            "ParameterValue": "YOUR-SECRET-INGEST-TOKEN" 
        },
        { 
            "ParameterKey": "HumioCloudWatchLogsAutoSubscription", 
            "ParameterValue": "true" 
        },
        { 
            "ParameterKey": "HumioCloudWatchLogsSubscriptionPrefix", 
            "ParameterValue": "humio" 
        },
        {
            "ParameterKey": "S3KeyNameForZipWithLambdas",
            "ParameterValue": "YOUR-ZIP-NAME.zip"
        }
    ]
    ```

    - Only the  `HumioIngestToken` parameter is required to be specified in the *parameters.json* file as the rest have default values.
    - The `S3KeyNameForZipWithLambdas` is important though, as this is were CloudFormation will look for the lambda files. Its default value should be that of the latest integration version, for example, *v1.0.0_cloudwatch2humio.zip*.

6. Create the stack using the CloudFormation file and the parameters that you have defined: 

    ```
    aws cloudformation create-stack --stack-name YOUR-DESIRED-STACK-NAME --template-body file://cloudformation.json --parameters file://parameters.json --capabilities CAPABILITY_IAM --region YOUR-REGION
    ```

    - `CAPABILITY_IAM` is the required value here. 

7. Upating the stack.

    - To update the stack, use the following command: 
    
        ```
        aws cloudformation update-stack --stack-name YOUR-DESIRED-STACK-NAME --template-body file://cloudformation.json --parameters file://parameters.json --capabilities CAPABILITY_IAM --region YOUR-REGION
        ```

    - Note: The stack will only register changes in the CloudFormation file or in the parameters' file. If you have updated the lambda files, you need to change the name of the zip file, and thus the parameter `S3KeyNameForZipWithLambdas` for your changes to be recognized.

8. Deleting the stack.

    - To delete the stack, use the following command:

        ```
        aws cloudformation delete-stack --stack-name YOUR-DESIRED-STACK-NAME
        ```

## Making a Pull Request
When you have made your changes locally, or you want feedback on a work in progress, you're almost ready to make a pull request. Before doing so however, please go through the following checklist:

1. Test the integration and make sure that all features are still functional.
2. Update the version number of the ZIP file in the `Makefile` and of the default value of the `S3KeyNameForZipWithLambdas` parameter in the `cloudformation.json` file. These should always match.
3. Update the `CHANGELOG.md`.
3. Add yourself to `AUTHORS.md`.

When you've been through the checklist, push your final changes to your development branch on GitHub.

Congratulations! Your branch is now ready to be included submitted as a pull requests. Got to [cloudwatch2humio](https://github.com/humio/cloudwatch2humio) and use the pull request feature to submit your contribution for review.

## For Maintainers: How to Release
When a new release of the integration needs to be uploaded to the S3 buckets hosting the lambda files, the version of the integration needs to be updated.

To update the version, follow these steps:

1. Make sure `CHANGELOG.md` has an entry for the new release version.
2. Locally, check out the `master` branch and pull from `origin/mater`.
3. Use __ to bump the project version.

    * To craete a patch run: ``
    * To create a minor run: ``
    * To create a major run: ``
    
4. Run `` to push changes.
5. Run the `deploy.sh` script. 

Terms of Service For Contributors
=================================
For all contributions to this repository (software, bug fixes, configuration changes, documentation, or any other materials), we emphasize that this happens under GitHubs general Terms of Service and the license of this repository.

## Contributing as an individual
If you are contributing as an individual you must make sure to adhere to:

The [GitHub Terms of Service](https://help.github.com/en/github/site-policy/github-terms-of-service) __*Section D. User-Generated Content,*__ [Subsection: 6. Contributions Under Repository License](https://help.github.com/en/github/site-policy/github-terms-of-service#6-contributions-under-repository-license):

_"Whenever you make a contribution to a repository containing notice of a license, you license your contribution under the same terms, and you agree that you have the right to license your contribution under those terms. If you have a separate agreement to license your contributions under different terms, such as a contributor license agreement, that agreement will supersede.
Isn't this just how it works already? Yep. This is widely accepted as the norm in the open-source community; it's commonly referred to by the shorthand "inbound=outbound". We're just making it explicit."_

## Contributing on behalf of a Corporation
If you are contributing on behalf of a Corporation you must make sure to adhere to:

The [GitHub Corporate Terms of Service](https://help.github.com/en/github/site-policy/github-corporate-terms-of-service) _**Section D. Content Responsibility; Ownership; License Rights,**_ [subsection 5. Contributions Under Repository License](https://help.github.com/en/github/site-policy/github-corporate-terms-of-service#5-contributions-under-repository-license):

_"Whenever Customer makes a contribution to a repository containing notice of a license, it licenses such contributions under the same terms and agrees that it has the right to license such contributions under those terms. If Customer has a separate agreement to license its contributions under different terms, such as a contributor license agreement, that agreement will supersede."_