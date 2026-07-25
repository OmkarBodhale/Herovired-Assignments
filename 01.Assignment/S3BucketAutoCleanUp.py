import boto3
from datetime import datetime, timezone

TARGET_BUCKET = "auto-s3-bucket-cleanup"
    
    # You can now easily change this value. 
    # E.g., 5 for 5 minutes, 0.5 for 30 seconds, 1440 for 24 hours.
CUSTOM_TIME_IN_MINUTES = 1440*30 

def cleanup_old_s3_objects(bucket_name, age_minutes=1.0):
    """
    Scans an S3 bucket and deletes objects older than the specified age.
    
    :param bucket_name: Name of the S3 bucket.
    :param age_minutes: Float or int representing the maximum age in minutes. 
                        Files older than this will be deleted.
    """
    s3_client = boto3.client('s3')
    now_utc = datetime.now(timezone.utc)
    
    # Convert the customizable minutes into seconds for accurate comparison
    max_age_seconds = age_minutes * 60
    
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name)
    
    objects_to_delete = []
    total_deleted = 0
    
    print(f"Scanning '{bucket_name}' for files older than {age_minutes} minute(s)...\n")
    
    for page in pages:
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            file_name = obj['Key']
            last_modified = obj['LastModified']
            
            # Calculate how old the file is in seconds
            age_in_seconds = (now_utc - last_modified).total_seconds()
            
            if age_in_seconds > max_age_seconds:
                print(f"Found expired file: {file_name} (Age: {age_in_seconds:.1f} seconds)")
                objects_to_delete.append({'Key': file_name})
                
                # Delete in batches of 1000
                if len(objects_to_delete) >= 1000:
                    response = s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    
                    # Print confirmation of deleted files
                    for deleted in response.get('Deleted', []):
                        print(f" -> Successfully deleted: {deleted.get('Key')}")
                        
                    total_deleted += len(response.get('Deleted', []))
                    objects_to_delete = []  # Reset batch
                    
    # Delete any remaining objects in the final batch
    if objects_to_delete:
        response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': objects_to_delete}
        )
        for deleted in response.get('Deleted', []):
            print(f" -> Successfully deleted: {deleted.get('Key')}")
            
        total_deleted += len(response.get('Deleted', []))
        
    print(f"\nCleanup complete. Total files deleted: {total_deleted}")


   
    
def lambda_handler(event, context):
    cleanup_old_s3_objects(TARGET_BUCKET, age_minutes=CUSTOM_TIME_IN_MINUTES)
