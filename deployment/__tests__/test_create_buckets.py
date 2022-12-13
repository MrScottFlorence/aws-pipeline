from deployment.src.create_buckets import Create_resources
from moto import mock_s3
import pytest
from unittest.mock import patch


@patch('deployment.src.create_buckets.os')
@mock_s3
def test_create_resource_creates_connection_on_instance_creation(os):
    """Mocking environment variables to mimic github secrets and mocking boto3, test that s3 exists"""
    os.environ.return_value = {'GITHUB_TOKEN':{
        'AWS_ACCESS_KEY':"temp",
        'AWS_SECRET_KEY':"tempSecret"}}
    creator = Create_resources()
    assert creator.s3 != None
    
