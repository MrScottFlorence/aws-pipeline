import os
import boto3
from botocore.exceptions import ClientError

class Deploy_lambdas():
    def __init__(self):
        self.create_aws_connection()
    
    def create_aws_connection(self):
        """Create the lambda client, using secrets obtained from github secrets"""
        try:
            if 'GITHUB_TOKEN' in os.environ:
                github_secrets: dict = os.environ['GITHUB_TOKEN']
                os.environ['AWS_ACCESS_KEY_ID'] = github_secrets['AWS_ACCESS_KEY']
                os.environ['AWS_SECRET_ACCESS_KEY'] = github_secrets['AWS_SECRET_KEY']

            self.s3 = boto3.client('lambda',
                                   region_name='us-east-1')
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
    