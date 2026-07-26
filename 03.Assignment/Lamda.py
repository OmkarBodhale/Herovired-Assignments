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
