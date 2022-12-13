import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


class Create_resources():
    def __init__(self):
        """Initialise the create resources class with the s3 connection started"""
        self.create_aws_connection()

    def create_aws_connection(self):
        """Create the s3 client, using secrets obtained from github secrets"""
        github_secrets: dict = os.environ['GITHUB_TOKEN']
        try:
            self.s3 = boto3.client('s3',
                                   region_name='us-east-1',
                                   aws_access_key_id=github_secrets['AWS_ACCESS_KEY'],
                                   aws_secret_access_key=github_secrets['AWS_SECRET_KEY'])
        except ClientError as ce:
            print(ce.response)
            
