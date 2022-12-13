import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import zipfile


class Create_resources():
    errors = []

    def __init__(self):
        """Initialise the create resources class with the s3 connection started"""
        self.create_aws_connection()

    def create_aws_connection(self):
        """Create the s3 client, using secrets obtained from github secrets"""
        try:
            if 'GITHUB_TOKEN' in os.environ:
                github_secrets: dict = os.environ['GITHUB_TOKEN']
                os.environ['AWS_ACCESS_KEY_ID'] = github_secrets['AWS_ACCESS_KEY']
                os.environ['AWS_SECRET_ACCESS_KEY'] = github_secrets['AWS_SECRET_KEY']

            self.s3 = boto3.client('s3',
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

    def create_s3_bucket(self, bucket_name: str):
        """Create a bucket of passed name if the name is valid"""
        try:
            self.s3.create_bucket(Bucket=bucket_name)
        except ClientError as ce:
            error = 'Client Error : ' + ce.response['Error']['Message']
            print(error)
            self.errors.append(error)

    def upload_lambda_function_code(self, folder_path: str, code_bucket: str, lambda_name: str):
        """Using a folder path, lambda name, and destination code bucket, zip the lambda into an archive and upload it to aws s3 bucket"""
        try:
            zip_directory(folder_path)
            with open("lambda.zip", "rb") as file:
                self.s3.upload_fileobj(file, code_bucket, lambda_name+".zip")
        except ClientError as nb:
            print(
                f"Bucket does not exist. Upload of {lambda_name} to {code_bucket} failed")
        except Exception as e:
            raise e


def zip_directory(folder_path: str):
    """Create a zip file, where the contents are at the top level where they would be with respect for their folder's path"""
    zip_file = zipfile.ZipFile("lambda.zip", 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            zip_file.write(os.path.join(root, file),
                           os.path.relpath(path=os.path.join(root, file),
                                           start=os.path.join(".", folder_path)))
