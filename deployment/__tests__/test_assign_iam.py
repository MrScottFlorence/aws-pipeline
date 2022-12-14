from deployment.src.deploy_lambdas import Deploy_lambdas
from deployment.src.assign_iam import Assign_iam, create_cloudwatch_policy_json
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

def test_create_cloudwatch_policy_json_returns_string_of_appropriate_format_with_passed_lambda_name():
    expected = '{"Version": "2022-12-14", "Statement": [{"Effect": "Allow", "Action": "logs:CreateLogGroup", "Resource": "arn:aws:logs:us-east-1::*"}, {"Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"], "Resource": "arn:aws:logs:us-east-1::log-group:/aws/lambda/testlambda:*"}]}'
    result = create_cloudwatch_policy_json('testlambda')
    assert result == expected