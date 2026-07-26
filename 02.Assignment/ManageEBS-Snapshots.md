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
2. **Create a EBS Volume** Configured the EBS Volume details and Click on Create Volume.
<img width="1902" height="856" alt="image" src="https://github.com/user-attachments/assets/bf6e8b21-62ba-45d2-af19-866ca2aea15f" />
<img width="1905" height="856" alt="image" src="https://github.com/user-attachments/assets/74309c28-441e-4669-9ba6-79e5ed06527c" />
3. **Lambda Deployment:** Create a Python Lambda function and apply the role. Set the following Environment Variables:
   * `VOLUME_ID`: The target EBS Volume ID (e.g., `vol-xxxxxxx`)
   * `RETENTION_DAYS`: `30`
4. **Deploy Code:** Paste the provided `boto3` script into the function source and deploy.
6. **EventBridge Trigger:** Create an EventBridge Schedule rule using the cron expression `cron(0 0 ? * SUN *)` and point the target to your Lambda function.
7. **Testing:** Manually trigger the Lambda function via the console. Verify in the EC2 Snapshots dashboard that a new snapshot is created with the tag `CreatedBy=Lambda-Backup`.

## Discussion: AWS Data Lifecycle Manager (DLM) vs. AWS Lambda

**Context:** AWS provides a native service called Data Lifecycle Manager (DLM) designed specifically to automate the creation, retention, and deletion of EBS snapshots based on tags. For most standard backup use cases, DLM is the recommended, zero-code solution.

**When is Custom Lambda Still the Better Choice?**
While DLM handles standard schedules effortlessly, a custom Lambda approach remains superior (or necessary) in the following scenarios:
1. **Custom Retention Logic:** If retention rules aren't strictly time-based (e.g., keeping the first snapshot of every month indefinitely, or retaining snapshots based on the time of day a deployment occurred), Lambda allows for arbitrary logic implementation.
2. **Cross-Account / Cross-Region Orchestration:** If a snapshot needs to be immediately copied to a disaster recovery account or a different region natively within the same workflow, Lambda can string these API calls together instantly.
3. **Pre/Post Automation Hooks:** If you need to freeze file systems, pause database writes (app-consistent backups), or send a custom notification payload to a Slack webhook upon backup completion, Lambda acts as the necessary glue. DLM only guarantees crash-consistent backups.
