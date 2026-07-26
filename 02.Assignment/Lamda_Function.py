import boto3
import os
import datetime
from dateutil.tz import tzutc

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    volume_id = os.environ['VOLUME_ID']
    retention_days = int(os.environ.get('RETENTION_DAYS', 30))
    
    # 1. Create a new snapshot
    create_response = ec2.create_snapshot(
        VolumeId=volume_id,
        Description=f'Automated weekly backup for {volume_id}',
        TagSpecifications=[{
            'ResourceType': 'snapshot',
            'Tags': [{'Key': 'CreatedBy', 'Value': 'Lambda-Backup'}]
        }]
    )
    
    new_snap_id = create_response['SnapshotId']
    print(f"Successfully created snapshot: {new_snap_id} for volume {volume_id}")

    # 2. Identify and clean up old snapshots
    cutoff_date = datetime.datetime.now(tzutc()) - datetime.timedelta(days=retention_days)
    
    # Filter for snapshots created by this function owned by this account
    describe_response = ec2.describe_snapshots(
        OwnerIds=['self'],
        Filters=[{'Name': 'tag:CreatedBy', 'Values': ['Lambda-Backup']}]
    )
    
    deleted_snapshots = []
    for snap in describe_response['Snapshots']:
        if snap['StartTime'] < cutoff_date:
            snap_id = snap['SnapshotId']
            ec2.delete_snapshot(SnapshotId=snap_id)
            deleted_snapshots.append(snap_id)
            
    if deleted_snapshots:
        print(f"Successfully deleted {len(deleted_snapshots)} old snapshots: {deleted_snapshots}")
    else:
        print("No snapshots older than the retention period were found. Skipping cleanup.")
        
    return {
        'statusCode': 200,
        'CreatedSnapshot': new_snap_id,
        'DeletedSnapshots': deleted_snapshots
    }
