import boto3
import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION')
EXTERNAL_S3_BUCKET = os.environ.get('EXTERNAL_S3_BUCKET')
s3 = boto3.client(
	's3', 
	aws_access_key_id=AWS_ACCESS_KEY_ID,
	aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
	region_name=AWS_REGION
)     
resp = s3.get_object(Bucket=EXTERNAL_S3_BUCKET, Key="freethrow.mov")  
print(resp)