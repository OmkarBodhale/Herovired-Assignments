# Public S3 Bucket Detector & SNS Alerter

## Objective

Detect any Amazon S3 bucket in the AWS account that is publicly accessible and automatically trigger an email alert via Amazon SNS.

*Note: Since April 2023, AWS enables Block Public Access (BPA) and disables ACLs by default for all new buckets. Therefore, this audit comprehensively checks the Block Public Access configuration, the bucket policy status (via the `IsPublic` flag), and legacy ACL grants.*

---

## Architecture Overview

1. **Amazon EventBridge:** Triggers the audit function on a daily schedule.
2. **AWS Lambda (Python/Boto3):** Iterates through all S3 buckets, interrogates their access configurations, and determines public exposure.
3. **Amazon SNS:** Receives alerts from Lambda and dispatches them to subscribed email addresses.

---

## Prerequisites

* An AWS Account with administrative or sufficient IAM privileges.
* An email address to receive security alerts.

---

## Step-by-Step Deployment Instructions

### 1. SNS Setup (Alerting)

1. Navigate to the **Amazon SNS** console.
2. Create a new **Topic**:
* Type: **Standard**
* Name: `PublicS3AlertTopic`


3. Once the topic is created, click **Create subscription**.
* Protocol: **Email**
* Endpoint: Enter your email address.


4. **Important:** Check your email inbox and click the **Confirm subscription** link sent by AWS.
5. Copy the **Topic ARN** (you will need this for the Lambda environment variables).

### 2. IAM Role Setup (Lambda Permissions)

1. Navigate to the **IAM** console and create a new **Role**.
2. Select **AWS service** as the trusted entity and choose **Lambda**.
3. Create and attach a new inline policy (or managed policy) with the following JSON:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3AuditPermissions",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketPublicAccessBlock",
                "s3:GetBucketPolicyStatus",
                "s3:GetBucketAcl"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SNSPublishPermissions",
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:REGION:ACCOUNT_ID:PublicS3AlertTopic"
        },
        {
            "Sid": "LambdaLogging",
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

*Note: Replace `REGION` and `ACCOUNT_ID` with your specific AWS details.*

### 3. Lambda Function Configuration

1. Navigate to the **AWS Lambda** console and click **Create function**.
2. Name the function `S3PublicBucketAuditor` and choose **Python 3.x** as the runtime.
3. Under **Permissions**, select **Use an existing role** and choose the IAM role created in Step 2.
4. Under the **Configuration** tab, go to **Environment variables** and add:
* Key: `SNS_TOPIC_ARN`
* Value: `[Your SNS Topic ARN from Step 1]`


5. Go to the **Code** tab and paste the following Boto3 script:

```python
import boto3
import os

s3 = boto3.client('s3')
sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    public_buckets = []
    
    try:
        response = s3.list_buckets()
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return {"status": "Error"}

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        is_public = False
        reasons = []

        # 1. Check Block Public Access Configuration
        try:
            pab = s3.get_public_access_block(Bucket=bucket_name)
            config = pab['PublicAccessBlockConfiguration']
            # If any of the 4 block settings are False, BPA is effectively disabled/partial
            if not (config.get('BlockPublicAcls') and config.get('IgnorePublicAcls') and 
                    config.get('BlockPublicPolicy') and config.get('RestrictPublicBuckets')):
                is_public = True
                reasons.append("Block Public Access is partially or fully disabled")
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                is_public = True
                reasons.append("No Block Public Access configuration found")
            else:
                print(f"Error checking PAB for {bucket_name}: {e}")

        # 2. Check Bucket Policy Status
        try:
            pol_status = s3.get_bucket_policy_status(Bucket=bucket_name)
            if pol_status['PolicyStatus']['IsPublic']:
                is_public = True
                reasons.append("Bucket Policy evaluates to Public")
        except s3.exceptions.ClientError as e:
            # NoSuchBucketPolicy is expected and fine
            if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                print(f"Error checking Policy Status for {bucket_name}: {e}")

        # 3. Check ACLs
        try:
            acl = s3.get_bucket_acl(Bucket=bucket_name)
            for grant in acl.get('Grants', []):
                uri = grant.get('Grantee', {}).get('URI', '')
                if uri in [
                    'http://acs.amazonaws.com/groups/global/AllUsers',
                    'http://acs.amazonaws.com/groups/global/AuthenticatedUsers'
                ]:
                    is_public = True
                    reasons.append("Public ACL found (AllUsers or AuthenticatedUsers)")
        except Exception as e:
            print(f"Error checking ACL for {bucket_name}: {e}")

        if is_public:
            public_buckets.append(f"- {bucket_name} \n  Flags: {', '.join(reasons)}")

    # Publish to SNS if public buckets exist
    if public_buckets:
        message_body = "URGENT: The following S3 buckets have public access enabled or Block Public Access disabled:\n\n"
        message_body += "\n\n".join(public_buckets)
        message_body += "\n\nPlease review these buckets immediately."
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="AWS Security Alert: Public S3 Buckets Detected",
            Message=message_body
        )
        print("Alert sent to SNS.")
        return {"status": "Alert triggered"}

    print("No public buckets found.")
    return {"status": "Secure"}

```

6. Click **Deploy**. Update the function timeout to at least 15-30 seconds (depending on the number of buckets in your account).

### 4. EventBridge Setup (Daily Scheduling)

1. Navigate to **Amazon EventBridge** and click **Create rule**.
2. Name the rule `DailyS3PublicBucketAudit`.
3. Choose **Schedule** as the rule type.
4. Set the schedule pattern to **A schedule that runs at a regular rate** (e.g., `1 Day`) or define a specific cron expression.
5. Under **Targets**, select **AWS Lambda function** and choose your `S3PublicBucketAuditor` function.
6. Save the rule.

---

## Testing & Validation

To ensure the automated alerts are working properly:

1. **Create a Test Bucket:**
* Name it `public-audit-test-bucket-[random-numbers]`.


2. **Expose the Bucket:**
* Go to the bucket's **Permissions** tab.
* Edit **Block public access (bucket settings)** and turn it **OFF**.
* Attach a bucket policy that grants public read access, for example:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::public-audit-test-bucket-[random-numbers]/*"
    }
  ]
}

```




3. **Trigger the Lambda:**
* Go to the Lambda console and click **Test** (you can use the default blank event template).


4. **Confirm Alert:**
* Check your email. You should receive a "Security Alert: Public S3 Buckets Detected" email naming the test bucket and listing the specific reasons (e.g., PAB disabled, Policy is Public).


5. **Clean Up:**
* **IMMEDIATELY** delete the test bucket or re-enable Block Public Access and remove the public bucket policy to re-secure your environment.
