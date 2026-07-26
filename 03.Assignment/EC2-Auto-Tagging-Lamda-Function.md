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
2. Create a new Lamda Function with meaning fullname having Python 3.14 runtime and deploy the code from Lamda.py file.
<img width="1910" height="862" alt="image" src="https://github.com/user-attachments/assets/785b21fc-0424-45ed-ad81-9598909911f7" />
<img width="1892" height="861" alt="image" src="https://github.com/user-attachments/assets/97caf045-78dc-4dd1-a0df-8949e0bd9755" />

3. Assign the IAM policy to the Lamda Function which we created in the step 1
<img width="1917" height="861" alt="image" src="https://github.com/user-attachments/assets/cbdefaac-83cc-47ce-9ebd-7410b4463289" />
<img width="1907" height="867" alt="image" src="https://github.com/user-attachments/assets/16990ace-764d-46e1-b047-eb4314dcbed6" />

4. Add a Event Bridge Trigger for the Lamda Function created in above step and assign below pattern.
```Json
   {
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"]
  }
}
```
<img width="1892" height="862" alt="image" src="https://github.com/user-attachments/assets/0ba4c820-94bc-4e37-9ba0-1e879e8bfa51" />
<img width="1902" height="862" alt="image" src="https://github.com/user-attachments/assets/54ae8c8c-37e3-43cf-b4b4-2235a8cee80a" />

5. Test the function by creating a ec2 instance wait for few minutes and once the ec2 is running check the tags for that instance.
   <img width="1912" height="862" alt="image" src="https://github.com/user-attachments/assets/e4213c5b-542d-464c-8cec-ebf425d11dbd" />
