import logging
import os
import traceback

import azure.functions as func

from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.ingest import (
    DataFormat,
    FileDescriptor,
    IngestionProperties,
    QueuedIngestClient
)
from azure.kusto.ingest.ingestion_properties import (
    IngestionMappingType,
)

ingest_uri = 'https://ingest-shieldai.westus2.kusto.windows.net'
tenant_id = os.environ['AZURE_AAD_TENANT_ID']
client_id = os.environ['AZURE_APP_CLIENT_ID']
client_secret = os.environ['AZURE_APP_CLIENT_SECRET']
kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
    ingest_uri, client_id, client_secret, tenant_id)

db = 'telemetry'
table = 'FlightEvents'
ingestion_props = IngestionProperties(
    database=db,
    table=table,
    data_format=DataFormat.CSV,
    flush_immediately=True,
    ingestion_mapping_type=IngestionMappingType.CSV,
    ingestion_mapping_reference='Mapping1',
)
client  = QueuedIngestClient(kcsb)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        for input_file in req.files.values():
            local_file_path = f'/tmp/{input_file.filename}'
            contents = input_file.stream.read()

            with open(local_file_path, 'wb') as f:
                f.write(contents)
            file_descriptor = FileDescriptor(local_file_path, os.path.getsize(local_file_path))
            result = client.ingest_from_file(file_descriptor, ingestion_properties=ingestion_props)

        return func.HttpResponse(
            f'Successfully queued all files for ingestion. Result: {repr(result)}',
            status_code=200
        )

    except Exception as e:
        logging.error(
            f'Failed to upload file {local_file_path}.'
            f'\nError: {e}'
            f'\nTraceback: {traceback.format_exc()}')
        return func.HttpResponse(
            f'Failed to upload file {local_file_path}.',
            status_code=418
        )
