import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


class Create_resources():
    errors = []
    def __init__(self):
        """Initialise the create resources class with the s3 connection started"""
        self.create_aws_connection()

    def create_aws_connection(self):
        """Create the s3 client, using secrets obtained from github secrets"""
        try:
            github_secrets: dict = os.environ['GITHUB_TOKEN']
            self.s3 = boto3.client('s3',
                                   region_name='us-east-1',
                                   aws_access_key_id=github_secrets['AWS_ACCESS_KEY'],
                                   aws_secret_access_key=github_secrets['AWS_SECRET_KEY'])
        except ClientError as ce:
            error = 'Client Error :' + ce.response['Error']['Message']
            print(error)
            self.errors.append(error)
        except AttributeError as ae:
            error = "Failed to find attributes 'AWS_ACCESS_KEY' and 'AWS_SECRET_KEY' on key 'GITHUB_TOKEN'"
            print(error)
            self.errors.append(error)
        except KeyError as ke:
            error = "Failed to find keys 'AWS_ACCESS_KEY' and 'AWS_SECRET_KEY' on key 'GITHUB_TOKEN'"
            print(error)
            self.errors.append(error)
        except Exception as e:
            print(e)
            self.errors.append(e)
            
    def create_s3_bucket(self,bucket_name:str):
        try : 
            self.s3.create_bucket(Bucket=bucket_name)
        except ClientError as ce:
            error = 'Client Error : ' + ce.response['Error']['Message']
            print(error)
            self.errors.append(error)
        
            
