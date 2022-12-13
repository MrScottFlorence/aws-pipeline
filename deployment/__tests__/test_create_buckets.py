from deployment.src.create_buckets import Create_resources
from moto import mock_s3
import pytest
from unittest.mock import patch
from botocore.exceptions import ClientError


@patch('deployment.src.create_buckets.os')
@mock_s3
def test_create_resource_creates_connection_on_instance_creation(os):
    """Mocking environment variables to mimic github secrets and mocking boto3, test that s3 exists"""
    os.environ.return_value = {'GITHUB_TOKEN':{
        'AWS_ACCESS_KEY':"temp",
        'AWS_SECRET_KEY':"tempSecret"}}
    creator = Create_resources()
    assert creator.s3 != None

@mock_s3
def test_create_resource_states_the_error_when_a_the_correct_github_secrets_have_not_been_made():
    """Testing the response when an access key is missing using mocked os response"""
    creator = Create_resources()
    result = creator.errors[0]
    assert result == "Failed to find keys 'AWS_ACCESS_KEY' and 'AWS_SECRET_KEY' on key 'GITHUB_TOKEN'"

@patch('deployment.src.create_buckets.boto3')
@patch('deployment.src.create_buckets.os')
def test_create_resource_states_when_a_user_error_such_as_invalid_password_has_been_made(os,boto):
    """Testing the response when an client error is raised on client creation by intercepting boto's client creation"""
    os.environ.return_value = {'GITHUB_TOKEN':{
        'AWS_ACCESS_KEY':"temp",
        'AWS_SECRET_KEY':"tempSecret"}}
    class patched_boto:
        def client(*,region_name,aws_access_key_id,aws_secret_access_key):
            raise ClientError(error_response={'Error':{'Message':'Client error content','Code':'123'}},operation_name="op")
    boto.return_value = patched_boto
    creator = Create_resources()
    result = creator.errors[0]
    assert result == ""
 