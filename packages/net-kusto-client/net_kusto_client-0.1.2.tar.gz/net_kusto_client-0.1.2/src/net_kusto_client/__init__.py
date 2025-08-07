import os
import json

from pathlib import Path
from azure.kusto.data import KustoConnectionStringBuilder, KustoClient
from azure.kusto.data.data_format import DataFormat
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties, FileDescriptor
from azure.kusto.data.helpers import dataframe_from_result_table

HOME_DIR = Path(os.path.expanduser('~'))
SETTINGS_FILE = Path(HOME_DIR) / "local.settings.json"
with open(SETTINGS_FILE, 'r') as f:
    jdata = json.load(f)
AAD_TENANT_ID = jdata['Values']['AAD_TENANT_ID']
CLUSTER = jdata['Values']['INGESTION_URI']
CLIENT_ID = jdata['Values']['CLIENT_ID']
CLIENT_SECRET = jdata['Values']['CLIENT_SECRET']
AUTHORITY_ID = jdata['Values']['AAD_TENANT_ID']
REGION = jdata['Values']['REGION']
CLUSTER_URI = jdata['Values']['CLUSTER_URI']
INGESTION_URI = jdata['Values']['INGESTION_URI']
KUSTO_URI = f"https://{CLUSTER_URI}.{REGION}.kusto.windows.net"
KUSTO_INGEST_URI = f"https://ingest-{INGESTION_URI}.{REGION}.kusto.windows.net"
KUSTO_DATABASE = jdata['Values']['KUSTO_DATABASE']


if CLIENT_SECRET:
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(KUSTO_URI, CLIENT_ID,
                                                                                     CLIENT_SECRET, AUTHORITY_ID)
    KCSB_INGEST_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(KUSTO_INGEST_URI, CLIENT_ID,
                                                                                            CLIENT_SECRET, AUTHORITY_ID)
else:
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(KUSTO_URI,
                                                                                              client_id=CLIENT_ID)
    KCSB_INGEST_DATA = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(KUSTO_INGEST_URI,
                                                                                                     client_id=CLIENT_ID)
# My example
EXAMPLE_KCSB_DATA = KustoConnectionStringBuilder.with_interactive_login(KUSTO_URI)
EXAMPLE_INGEST_KCSB_DATA = KustoConnectionStringBuilder.with_interactive_login(KUSTO_INGEST_URI)
EXAMPLE_FILE = Path(HOME_DIR) / "example.csv"
EXAMPLE_KUSTO_TABLE = jdata['Values']['EXAMPLE_KUSTO_TABLE']

# Storm Events Example
SAMPLE_KUSTO_URI = "https://help.kusto.windows.net/"
SAMPLE_KUSTO_DATABASE = "Samples"
SAMPLE_KCSB = KustoConnectionStringBuilder.with_interactive_login(SAMPLE_KUSTO_URI)


class NetKustoClient:
    def __init__(self):
        self.ingest_client = QueuedIngestClient(KCSB_INGEST_DATA)
        self.client = KustoClient(KCSB_DATA)
        self.example_client = KustoClient(EXAMPLE_KCSB_DATA)
        self.example_ingest_client = QueuedIngestClient(EXAMPLE_INGEST_KCSB_DATA)
        self.storm_events_sample_client = KustoClient(SAMPLE_KCSB)
    
    def create_table(self, table_name, column_names):
        try:
            # Example column_names:str = DeviceName: string, OSVersion: string
            CREATE_TABLE_COMMAND  = f""".create table {table_name} ({column_names})"""
            RESPONSE = self.client.execute_mgmt(KUSTO_DATABASE, CREATE_TABLE_COMMAND)
            dataframe_from_result_table(RESPONSE.primary_results[0])
        except KustoServiceError as err:
            print("Error creating table:", err)
    
    def ingest_data(self, table_name, file_path):
        try:
            if table_name:
                ingestion_properties = IngestionProperties(
                    database=KUSTO_DATABASE,
                    table=table_name,
                    data_format=DataFormat.CSV,
                )
                if not os.path.isfile(file_path):
                    print(f"File {file_path} does not exist.")
                    return
                file_descriptor = FileDescriptor(str(file_path))
                self.ingest_client.ingest_from_file(file_descriptor, ingestion_properties)
                print(f"Ingestion of {file_path} to table deviceinfo in database {KUSTO_DATABASE} initiated successfully.")
        except KustoServiceError as err:
            print("Error ingesting data:", err)
    
    def execute_take_ten_query(self, table_name):
        try:
            if table_name:
                query = f"{table_name} | take 10"
                response = self.client.execute_query(KUSTO_DATABASE, query)
                df = dataframe_from_result_table(response.primary_results[0])
                return df
        except KustoServiceError as err:
            print("Error executing query:", err)
    
    def execute_query(self, query):
        try:
            if query:
                response = self.client.execute_query(KUSTO_DATABASE, query)
                df = dataframe_from_result_table(response.primary_results[0])
                return df
        except KustoServiceError as err:
            print("Error executing query:", err)

    def create_sample_table(self):
        try:
            CREATE_TABLE_COMMAND  = f""".create table {EXAMPLE_KUSTO_TABLE} (DeviceName: string, OSVersion: string)"""
            RESPONSE = self.example_client.execute_mgmt(KUSTO_DATABASE, CREATE_TABLE_COMMAND)
            dataframe_from_result_table(RESPONSE.primary_results[0])
        except KustoServiceError as err:
            print("Error creating table:", err)

    def ingest_sample_data(self):
        try:
            ingestion_properties = IngestionProperties(
                database=KUSTO_DATABASE,
                table=EXAMPLE_KUSTO_TABLE,
                data_format=DataFormat.CSV,
            )
            file_descriptor = FileDescriptor(str(EXAMPLE_FILE))
            self.example_ingest_client.ingest_from_file(file_descriptor, ingestion_properties)
            print(f"Ingestion of {EXAMPLE_FILE} to table deviceinfo in database {KUSTO_DATABASE} initiated successfully.")
        except KustoServiceError as err:
            print("Error ingesting data:", err)

    def execute_sample_query(self):
        try:
            query = f"{EXAMPLE_KUSTO_TABLE} | take 10"
            response = self.example_client.execute_query(KUSTO_DATABASE, query)
            df = dataframe_from_result_table(response.primary_results[0])
            print(df)
        except KustoServiceError as err:
            print("Error executing query:", err)

    def execute_stormevents_sample_query(self):
        try:
            query = "StormEvents | take 10"
            response = self.storm_events_sample_client.execute_query(SAMPLE_KUSTO_DATABASE, query)
            df = dataframe_from_result_table(response.primary_results[0])
            print(df)
        except KustoServiceError as err:
            print("Error executing query:", err)
