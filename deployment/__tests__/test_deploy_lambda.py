from deployment.src.deploy_lambdas import Deploy_lambdas
from deployment.src.create_buckets import Create_resources, zip_directory
from moto import mock_lambda
from unittest.mock import patch
import pytest

@pytest.mark.skip("Test requires iam roles setup")
@mock_lambda
def test_create_lambda_successfully_deploys_when_zip_is_available():
    create = Create_resources()
    create.create_s3_bucket("code-bucket")
    create.upload_lambda_function_code(code_bucket="code-bucket",folder_path="deployment/__tests__/test_data/lambda1",lambda_name="customLambda")
    deploy = Deploy_lambdas()
    deploy.create_lambda(lambda_name="customLambdaName",code_bucket="code-bucket",role_arn="",zip_file="customLambda.zip")
    result = deploy.lambda_client.list_functions()
    print(result)
    assert 0 == 1