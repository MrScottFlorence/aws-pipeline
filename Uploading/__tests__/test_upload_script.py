import pytest
import pandas as pd
from src.Uploading_main import get_parquet_data, creating_insert_string
from src.Upload_Helpers import get_credentials
import os
import boto3
from moto import mock_s3
from botocore.exceptions import ClientError
import time



@mock_s3
def test_get_parquet_data():
    '''Uploads a file, downloads it, checks that the csv df is equal to parquet one such that 
    the correct file was obtained
    '''
    bucket_name = 'test_bucket'
    key = 'test/sales/test'
    # create a test S3 bucket
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket=bucket_name)

    # loads a parquet file into a data fram, then put it into the bucket as parquet format
    data = pd.read_parquet('data/test_sample.parquet')
    conn.Object(bucket_name, key).put(Body=data.to_parquet())

    # run the function
    get_parquet_data(bucket_name, key)

    # assert that the output csv file was created in local memory
    assert os.path.isfile('output.csv') == True

    # assert that the contents of the csv file match the expected contents
    expected_df = pd.read_parquet('data/test_sample.parquet')
    output_df = pd.read_csv('output.csv')
    pd.testing.assert_frame_equal(output_df, expected_df)
    

@mock_s3
def test_get_parquet_data_with_large_file():
    '''Tests the function performance when it tries to download a large file'''
    # create a test S3 bucket
    conn = boto3.resource('s3', region_name='us-east-1')
    bucket_name = 'test_bucket'
    conn.create_bucket(Bucket=bucket_name)

    # upload a large parquet file to the test S3 bucket
    key = 'test/sales/large_file'
    data = pd.read_csv('data/large_file.csv')
    conn.Object(bucket_name, key).put(Body=data.to_parquet())

    # measure the execution time of the function
    start = time.time()
    get_parquet_data(bucket_name, key)
    end = time.time()
    execution_time = end - start

    # assert that the output csv file was created in local memory
    assert os.path.isfile('output.csv') == True

    # assert that the function execution time is below a threshold of 3 seconds
    threshold = 3
    assert execution_time < threshold


def test_creating_insert_string_produces_correct_length_query_string():
    # testing with specified string_count = 3
    string_count = 3
    expected_result = "INSERT INTO specific_table VALUES ( %s, %s, %s )"
    assert creating_insert_string(string_count) == expected_result


def test_creating_insert_string_raises_error():
    # testing with string_count = None
    with pytest.raises(TypeError):
        creating_insert_string(None)

    # testing with string_count = -1
    with pytest.raises(ValueError):
        creating_insert_string(-1)


# @pytest.fixture
# def dataframe():
#     return pd.DataFrame({'col1':[1,2,3],'col2':[4,5,6]})

# def test_get_row_values(dataframe):
#     data = []
#     get_row_values(dataframe)
#     for index, row in dataframe.iterrows():
#         row_data = tuple(row)
#         data.append(row_data)
#     assert data == [(1, 4), (2, 5), (3, 6)]

# def test_get_row_values_empty_dataframe():
#     dataframe = pd.DataFrame()
#     with pytest.raises(ValueError) as e:
#         get_row_values(dataframe)
#     assert str(e.value) == "Dataframe is empty"

# def test_get_row_values_dataframe_with_string_columns():
#     dataframe = pd.DataFrame({'col1':['a','b','c'],'col2':['d','e','f']})
#     with pytest.raises(TypeError) as e:
#         get_row_values(dataframe)
#     assert str(e.value) == "Dataframe has string columns"