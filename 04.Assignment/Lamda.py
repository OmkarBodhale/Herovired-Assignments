import boto3
import datetime
import os

def lambda_handler(event, context):
    # Fetch from environment variables with safe defaults
    monthly_cost = float(os.environ.get('THRESHOLD_COST', '10.0'))
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:123456789012:MyTopic')

    ce = boto3.client('ce')
    sns = boto3.client('sns')

    today = datetime.datetime.now(datetime.UTC).date()
    
    # Start date is the 1st of the current month
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    
    # End date must be exclusive (tomorrow) to include today's cost
    end_date = (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")

    # Query Cost Explorer
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=[
            'UnblendedCost',
        ]
    )

    # Extract the amount
    amount_str = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    amount = float(amount_str)
    
    print(f"Total Cost: ${amount:.2f}")

    # Compare and Alert
    if amount > monthly_cost:
        message = f"Your AWS monthly cost has exceeded the threshold of ${monthly_cost}. Current cost is ${amount:.2f}."
        print(message)
        
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject='AWS Cost Alert'
        )
        return {"status": "Alert sent"}
        
    return {"status": "Under threshold"}
