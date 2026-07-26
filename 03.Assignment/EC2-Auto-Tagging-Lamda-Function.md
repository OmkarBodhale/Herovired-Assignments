# Automated EC2 Instance Tagging via AWS Lambda & EventBridge

## 📌 Overview
This project automates the tagging of newly launched Amazon EC2 instances. In cloud environments, enforcing consistent tagging policies (such as `LaunchDate`, `Environment`, and `Owner`) is critical for cost allocation, resource tracking, and security accountability. 

This repository documents two approaches:
1. **Standard Approach:** Triggers on EC2 state-change notifications.
2. **Advanced Approach (CloudTrail):** Triggers on the `RunInstances` API call to automatically extract the IAM user who launched the instance and assign them as the `Owner`.

---

## 🏗 Architecture
1. **Trigger:** A user or pipeline launches a new EC2 instance.
2. **Event Router:** AWS EventBridge detects the launch via a State Change or an API call (CloudTrail).
3. **Compute:** EventBridge invokes an AWS Lambda function, passing the event details as a JSON payload.
4. **Action:** The Lambda function (Python/Boto3) parses the instance ID and applies predefined tags via the EC2 API.
5. **Logging:** Execution details and errors are logged to AWS CloudWatch.

---

## Steps :
1. Create a IAM policy for the lamda fuction with below mentioned defination.
## 🔐 IAM Role Permissions
The Lambda function requires an Execution Role with the following inline policy to interact with EC2 and write logs to CloudWatch.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowEC2Tagging",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateTags",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowCloudWatchLogging",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```
<img width="1902" height="867" alt="image" src="https://github.com/user-attachments/assets/86d46c2f-56f5-49ed-988c-29caf7ce5302" />
2. Create a new Lamda Function and deploy the below code.
```
import boto3
import logging
import datetime

client = boto3.client('ec2')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        instanceId = event['detail']['instance-id']
        logger.info(f"Processing RunInstances event for instance: {instanceId}")

        currentTimestamp = datetime.datetime.now().strftime("%Y-%m-%d")

        tags=[
        {'Key': 'LaunchDate','Value': currentTimestamp,},
        {'Key': 'Environment','Value': 'production',},]
        response = client.create_tags(Resources=[instanceId,],Tags=tags,)
        logger.info(f"Successfully tagged instance {instanceId} with LaunchDate and Environment tags.")
        return {
            'statusCode': 200,
            'body': f"Successfully tagged instance {instanceId} with LaunchDate and Environment tags."
        }
        
    except Exception as e:
        logger.error(f"Error processing RunInstances event: {str(e)}")
        raise e
 ```

  3. Assign the IAM policy to the Lamda Function which we created in the step 1
