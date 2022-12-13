from deployment.src.deploy_lambdas import Deploy_lambdas
from deployment.src.assign_iam import Assign_iam
from moto import mock_iam
from unittest.mock import patch
import pytest



@patch('deployment.src.create_buckets.os')
@mock_iam
def test_create_resource_creates_connection_on_instance_creation(os):
    """Mocking environment variables to mimic github secrets and mocking boto3, test that iam connection exists"""
    os.environ.return_value = {'GITHUB_TOKEN': {
        'AWS_ACCESS_KEY': "temp",
        'AWS_SECRET_KEY': "tempSecret"}}
    permissions = Assign_iam()
    assert permissions.iam != None