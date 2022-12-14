import os
import boto3
from botocore.exceptions import ClientError
import json

class Assign_iam():
    aws_lambda_execution_policy = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
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

    def create_lambda_role(self,role_name:str):
        """Sets up role of passed name, with the ability of a lambda function to assume said role"""
        lambda_role_document = '{"Version": "2022-12-14","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"},"Action": "sts:AssumeRole"}]}'
        response = self.iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument = lambda_role_document
        )
        return response
    def attach_execution_role(self,role_name:str):
        """Attaches the AWS lambda execution policy to the passed role"""
        response = self.iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        return response
    def create_policies(self,lambda_name:str,ingest_bucket:str,processed_bucket:str):
        cloudwatch_policy_response = self.iam.create_policy(
            PolicyName=f'cloudwatch_policy-{lambda_name}',
            PolicyDocument=create_cloudwatch_policy_json(lambda_name),
            Description=f'Cloudwatch policy for {lambda_name}'
        )
        s3_ingest_read_access_response = self.iam.create_policy(
            PolicyName=f's3-read-bucket-{lambda_name}',
            PolicyDocument=create_s3_access_policy_json(ingest_bucket,list=True, get=True),
            Description=f'Read the ingest bucket policy policy for {lambda_name}'
        )
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

def create_s3_access_policy_json(bucket:str,list:bool=False,get:bool=False,put:bool=False):
    """Creates a policy document for access to a given bucket, and only the required action permissions"""
    policy_document = {
        "Version": "2022-12-14",
        "Statement": []
    }
    if list :
        policy_document["Statement"].append({
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket}"
                ]
            })
    if get : 
        policy_document["Statement"].append(
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket}/*"
                ]
            })
    if put : 
        policy_document["Statement"].append(
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket}/*"
                ]
            })
    return json.dumps(policy_document)