# Automated EBS Snapshot Creation and Cleanup

## Objective
A serverless automation utility built with AWS Lambda and Amazon EventBridge to automatically create weekly backups (snapshots) of a designated Elastic Block Store (EBS) volume, tag them for tracking, and safely delete snapshots that exceed a 30-day retention period.

## Architecture
* **Amazon EventBridge:** Triggers the automation workflow on a weekly cron schedule.
* **AWS Lambda (Python 3.x / Boto3):** Executes the business logic to create, tag, filter, and delete snapshots.
* **AWS IAM:** Applies least-privilege permissions allowing Lambda to interface with EC2 resources.
* **Amazon EC2/EBS:** The target storage infrastructure being backed up.

## Prerequisites
* An active AWS Account.
* An existing EC2 EBS Volume.
* IAM permissions to create Roles, Policies, Lambda Functions, and EventBridge rules.

## Setup Instructions

1. **IAM Role Configuration:** Create an IAM Role for Lambda with `AWSLambdaBasicExecutionRole` and an inline policy granting `ec2:CreateSnapshot`, `ec2:DescribeSnapshots`, `ec2:DeleteSnapshot`, and `ec2:CreateTags`.
Note : You need to replace the Region, Account Id and Volume Id in the policy and then apply "arn:aws:ec2:REGION:ACCOUNT_ID:volume/YOUR_VOLUME_ID"
<img width="1902" height="862" alt="image" src="https://github.com/user-attachments/assets/b9f9de7d-73a6-4102-a391-7c2956a26e42" />

2. **Create a EBS Volume** Configured the EBS Volume details and Click on Create Volume.
<img width="1902" height="856" alt="image" src="https://github.com/user-attachments/assets/bf6e8b21-62ba-45d2-af19-866ca2aea15f" />
<img width="1905" height="856" alt="image" src="https://github.com/user-attachments/assets/74309c28-441e-4669-9ba6-79e5ed06527c" />
3. **Lambda Deployment:** Create a Python Lambda function and apply the role. Set the following Environment Variables:
   * `VOLUME_ID`: The target EBS Volume ID (e.g., `vol-xxxxxxx`)
   * `RETENTION_DAYS`: `30`
<img width="1897" height="857" alt="image" src="https://github.com/user-attachments/assets/89f4e602-8abd-4318-ae86-389020149e8b" />
4. Configure the IAM role created in the step 1
<img width="1907" height="862" alt="image" src="https://github.com/user-attachments/assets/db595474-b554-4f32-91b7-8ee3c17d6172" />
<img width="1897" height="862" alt="image" src="https://github.com/user-attachments/assets/b625c00e-d2a4-489b-b8d9-dbfbda81dc46" />

4. **Deploy Code:** Copy the Boto3 Script from Lamda_Function.py file and deploy.
<img width="1900" height="857" alt="image" src="https://github.com/user-attachments/assets/b99fc0fa-b94f-474b-a4b5-32ee9c8d91b1" />
<img width="1917" height="867" alt="image" src="https://github.com/user-attachments/assets/1d65b7e1-9336-407f-adf0-549f95e7497d" />
Deleting older Snapshot ---Here I have configured the retention days as 0.5 to test
<img width="1891" height="852" alt="image" src="https://github.com/user-attachments/assets/a0649507-b3a1-4ee2-8635-68c96acf3a6f" />

6. **EventBridge Trigger:** Create an EventBridge Schedule rule using the cron expression `cron(0 0 ? * SUN *)` and point the target to your Lambda function.
<img width="1897" height="870" alt="image" src="https://github.com/user-attachments/assets/c0ea6229-30b7-4d96-8fa2-8170d6715b1a" />
<img width="1906" height="866" alt="image" src="https://github.com/user-attachments/assets/49f95488-b728-401b-9dcf-9e5d8ff2d787" />

   **Note :** Set Schedule pattern as `cron(0 0 ? * SUN *)` this will trigger this automaically every sunday.

## Discussion: AWS Data Lifecycle Manager (DLM) vs. AWS Lambda

**Context:** AWS provides a native service called Data Lifecycle Manager (DLM) designed specifically to automate the creation, retention, and deletion of EBS snapshots based on tags. For most standard backup use cases, DLM is the recommended, zero-code solution.

**When is Custom Lambda Still the Better Choice?**
While DLM handles standard schedules effortlessly, a custom Lambda approach remains superior (or necessary) in the following scenarios:
1. **Custom Retention Logic:** If retention rules aren't strictly time-based (e.g., keeping the first snapshot of every month indefinitely, or retaining snapshots based on the time of day a deployment occurred), Lambda allows for arbitrary logic implementation.
2. **Cross-Account / Cross-Region Orchestration:** If a snapshot needs to be immediately copied to a disaster recovery account or a different region natively within the same workflow, Lambda can string these API calls together instantly.
3. **Pre/Post Automation Hooks:** If you need to freeze file systems, pause database writes (app-consistent backups), or send a custom notification payload to a Slack webhook upon backup completion, Lambda acts as the necessary glue. DLM only guarantees crash-consistent backups.
