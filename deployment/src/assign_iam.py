import os
import boto3
from botocore.exceptions import ClientError
import json

class Assign_iam():
    
    def __init__(self):
        self.create_aws_connection()
        
    def create_aws_connection(self):
        """Create the lambda client, using secrets obtained from github secrets"""
        try:
            if 'GITHUB_TOKEN' in os.environ:
                github_secrets: dict = os.environ['GITHUB_TOKEN']
                os.environ['AWS_ACCESS_KEY_ID'] = github_secrets['AWS_ACCESS_KEY']
                os.environ['AWS_SECRET_ACCESS_KEY'] = github_secrets['AWS_SECRET_KEY']

            self.iam = boto3.client('iam',
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
    
    def create_policies(self):
        #s3 access policy
        #lambda execution policy
        #cloudwatch policy
        #store policy details to class
        pass
    
    def create_roles(self):
        #Execution role
            #Attach ingest bucket for getting source
            #Attach processed bucket for saving output
        pass
    def give_lambda_log_permissions(self, log_arn:str):
        pass
    def give_lambda_s3_bucket_permissions(self,bucket_name:str):
        pass
    def give_lambda_invoke_permissions(self,lambda_name:str):
        pass

def create_cloudwatch_policy_json(lambda_name:str):
    cloudwatch_log_policy = { 
        "Version": "2022-12-14",
        "Statement": [ 
                {"Effect": "Allow",
                 "Action": "logs:CreateLogGroup", 
                 "Resource": "arn:aws:logs:us-east-1::*" 
                }, 
                {"Effect": "Allow",
                 "Action": [ "logs:CreateLogStream", "logs:PutLogEvents" ], 
                 "Resource": f"arn:aws:logs:us-east-1::log-group:/aws/lambda/{lambda_name}:*" 
                } 
            ] 
        }
    return json.dumps(cloudwatch_log_policy)