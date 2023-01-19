import boto3
import io 
import pandas as pd 
import psycopg2
import re
import logging
from Upload_Helpers import get_credentials
import pyarrow

credentials = get_credentials('postgres_credentials')

conn = psycopg2.connect(database="postgres", user=credentials[0], 
password=credentials[1], host=credentials[2], port="5432")

all_table_names = ['dim_counterparty', 'dim_currency', 'dim_date', 'dim_design', 'dim_location',
'dim_payment_type', 'dim_staff', 'dim_transaction', 'fact_payment', 'fact_purchase_order', 'fact_sales_order']
cur = conn.cursor()
bucket_name = 'bosch-test-run-2-processed-bucket'
file_key = 'Ben-Test/Sales-Parquet/date/RunNum:331.parquet'


def get_parquet_data(bucket_name, key):
    '''Downloads data from ingested bucket in parquet format and then saves it locally to a csv'''
    try:
        buffer = io.BytesIO()
        client = boto3.resource('s3', aws_access_key_id=credentials[4], aws_secret_access_key=credentials[5])
        object = client.Object(bucket_name, key)
        object.download_fileobj(buffer)

        
        df = pd.read_parquet(buffer)
        df.to_csv('output.csv', index=False)
        return df
    except Exception as e:
        logging.error(f"An error occurred while downloading the file: {e}")
        raise e


def set_table_to_update():
    '''Uses a regex of the file_key to determine the name of the table in question, then iterates
    over all the table names until it finds the specific table, then sets that as the global variable
    so that the rest of the file can use it 
    If either the file key or table to update is not correct then valueErrors are raised

    Use of any() to check if at least one name matches 
    Use of next() to get the first table name in the generator expression. More efficient 
    than using a list - Helps scalability. 
    '''
    try:
        logging.info('setting table to use')
        match = re.search(r'/.*?/([^/]+)', file_key)

        if not match:
            raise ValueError("file_key does not match the expected format")

        table_to_update = match.group(1)

        if not any(table_to_update in table_name.split('_') for table_name in all_table_names):
            raise ValueError(f"{table_to_update} not found in list of all table names")

        global specific_table
        specific_table = next(table_name for table_name in all_table_names if table_to_update in table_name.split('_'))

    except Exception as e:
        logging.error(f"An error occurred while setting the table: {e}")
        raise e

def creating_insert_string(string_count):
    '''Makes a way to change the amount of values placeholders so that the insert
    works for any of the incoming tables, string count is equal to columns and
    thats how many placeholders you will need. 

    Need individual query string for each table because different amount of values  
    Raises error if input is incorrect 
    ''' 
    logging.info('Creating insert query string with length:', string_count)
    try:
        insert_string = 'INSERT INTO {} VALUES ( %s )'         
        placeholderStr = insert_string.split("%s")

        changing_query_string = placeholderStr[0] + "%s, " * string_count + placeholderStr[1] 
        index = changing_query_string.rfind(",")    

        final_string = str(changing_query_string[:index] + changing_query_string[index+1:]).format(specific_table)
        logging.info('This is the query string', final_string)

        return final_string

    except TypeError as Te:
        logging.error(Te)
        raise Te
    except ValueError as Ve:
        logging.error(Ve)
        raise Ve


def insert_row_data(data, df):
    '''Inserts rows of data into the specific table in the data warehouse
    after creating the query string for specific table

    Updates the warehouse by deleting all the present data and then overwriting it with the new table
    '''

    string_count=0
    columns = df.columns
    for column in columns:
        string_count+=1
    insertString = creating_insert_string(string_count)

    delete = 'DELETE FROM {}'.format(specific_table)
    insert = insertString
    cur.execute(delete)
    conn.commit()

    for row in data:
        logging.info(f'Inserting row {row}')
        cur.execute(insert, row)
        conn.commit()


def get_row_values(dataframe):
    '''Gets all the rows of data within the downloaded dataframe and then starts the insertion process'''
    data = []

    for index, row in dataframe.iterrows():
        row_data = tuple(row)
        data.append(row_data)

    insert_row_data(data, dataframe)



dataframe = get_parquet_data(bucket_name=bucket_name, key=file_key)
set_table_to_update()
get_row_values(dataframe)


cur.close()
conn.close()
















