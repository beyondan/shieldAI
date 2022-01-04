import logging
import os
import pandas
import traceback

import azure.functions as func

from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties, DataFormat
from azure.kusto.ingest.ingestion_properties import (
    IngestionMappingType,
    ReportLevel
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
    body = req.get_json()
    rows = body.get('data')
    df = pandas.DataFrame(data=rows)

    try:
        logging.info('Sending ingest request...')
        client.ingest_from_dataframe(df, ingestion_properties=ingestion_props)
        return func.HttpResponse(
            'Successfully queued all flight data for ingestion.',
            status_code=200
        )

    except Exception as e:
        logging.error(
            f'Failed to queue flight data for ingestion.'
            f'\nError: {e}'
            f'\nTraceback: {traceback.format_exc()}'
        )
        return func.HttpResponse(e, status_code=418)
