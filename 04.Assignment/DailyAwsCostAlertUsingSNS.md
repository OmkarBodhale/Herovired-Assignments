# Daily AWS Cost Alert Using Cost Explorer API and SNS

## Objective

Build an automated alert system that triggers when your AWS Month-to-Date (MTD) spend exceeds a predefined threshold.

> **Note on Architecture:** The old CloudWatch "Billing" metric is legacy — it only exists in the `us-east-1` region and must be manually enabled. This project uses the modern, enterprise-standard approach: the **AWS Cost Explorer API (`ce:GetCostAndUsage`)**.

---

## Architecture Overview

1. **Amazon EventBridge** triggers the Lambda function on a daily schedule.
2. **AWS Lambda** queries the **AWS Cost Explorer API** for the current month-to-date `UnblendedCost`.
3. If the cost exceeds the threshold, Lambda publishes a message to an **Amazon SNS** topic.
4. **Amazon SNS** delivers the alert to subscribed email addresses.

---

## 🛠️ Step-by-Step Implementation

### Step 1: SNS Setup

1. Navigate to **Amazon SNS** in the AWS Console.
2. Create a new **Standard Topic** (e.g., `aws-cost-alerts`).
3. Create a **Subscription** for the topic:
* **Protocol:** Email
* **Endpoint:** Your email address


4. Check your inbox and **Confirm the subscription**.

### Step 2: IAM Role Configuration

Create a new IAM Role for your Lambda function. Attach an inline policy granting permissions to query the Cost Explorer API and publish to your specific SNS topic:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ce:GetCostAndUsage",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:REGION:ACCOUNT_ID:aws-cost-alerts"
        }
    ]
}

```

*(Also attach the AWS managed `AWSLambdaBasicExecutionRole` so the function can write logs to CloudWatch).*

### Step 3: Lambda Function (Boto3)

Create a Python 3.x Lambda function, attach the IAM role from Step 2, and add the following code:

```python
import boto3
import os
from datetime import date

def lambda_handler(event, context):
    ce = boto3.client('ce')
    sns = boto3.client('sns')
    
    # Configure via Environment Variables
    THRESHOLD = float(os.environ.get('THRESHOLD', '50.0'))
    SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
    
    # Calculate MTD date range
    today = date.today()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Cost Explorer API requires a minimum 1-day range
    if start_date == end_date:
        print("First day of the month. Skipping evaluation.")
        return {"statusCode": 200, "body": "Skipped"}
        
    # Query Cost Explorer
    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    
    cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
    print(f"Current Month-to-Date Cost: ${cost:.2f}")
    
    # Alert Logic
    if cost > THRESHOLD:
        message = f"🚨 AWS Cost Alert: Month-to-date spend is ${cost:.2f}, exceeding the threshold of ${THRESHOLD}."
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="AWS Spend Limit Exceeded",
            Message=message
        )
        print("Threshold exceeded. SNS Alert sent.")
        
    return {"statusCode": 200, "body": f"Processed cost: ${cost}"}

```

**Environment Variables Required:**

* `THRESHOLD`: e.g., `50.0`
* `SNS_TOPIC_ARN`: The ARN of your SNS topic from Step 1.

### Step 4: EventBridge Scheduling

1. Navigate to **Amazon EventBridge** > **Rules** > **Create rule**.
2. Select **Schedule** and set it to run daily (e.g., `cron(0 12 * * ? *)` for 12:00 PM UTC).
3. Set the target to your **Lambda function**.

### Step 5: Testing

To ensure the pipeline works:

1. Temporarily lower the `THRESHOLD` environment variable in your Lambda function to `$0.01`.
2. Click **Test** in the Lambda console.
3. Check CloudWatch logs to see the retrieved amount printed.
4. Verify you received the email alert from SNS.
5. Restore the `THRESHOLD` to your actual budget limit.

---

## 🧠 Design Discussion: Managed vs. Custom Solutions

In an enterprise environment or technical interview, you should be able to justify why you built a custom solution instead of using native tools.

**AWS Budgets (The Managed Alternative):**
AWS natively offers AWS Budgets, which requires no code, integrates with SNS/Chatbot natively, and can even trigger actions (like shutting down EC2 instances) when thresholds are crossed. For simple total-cost alerts, AWS Budgets is the recommended best practice.

**When Custom Lambda Logic Wins:**
You should implement a Lambda/Cost Explorer architecture over AWS Budgets when you need highly custom routing or logic, such as:

* **Complex Anomaly Logic:** Triggering alerts only if spend spikes by X% on a weekend.
* **Granular Breakdowns:** Fetching the top 3 most expensive services of the day and including them in the alert body.
* **Custom Integrations:** Formatting the payload as rich JSON to send to a third-party API, specific Slack/Teams webhooks, or an internal ticketing system (like Jira/ServiceNow) where AWS Chatbot is insufficient.
