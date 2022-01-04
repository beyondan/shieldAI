import logging
import os
import traceback

import azure.functions as func

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cluster = "https://shieldai.westus2.kusto.windows.net"
        tenant_id = os.environ['AZURE_AAD_TENANT_ID']
        client_id = os.environ['AZURE_APP_CLIENT_ID']
        client_secret = os.environ['AZURE_APP_CLIENT_SECRET']

        kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
            cluster, client_id, client_secret, tenant_id)

        client = KustoClient(kcsb)
        db = "telemetry"
        query = req.get_json().get('query')

        logging.info(f'Executing query:\n{query}')
        response = client.execute_query(db, query)

        df = dataframe_from_result_table(response.primary_results[0])
        return func.HttpResponse(df.to_json(), status_code=200)
    except Exception as e:
        logging.error(
            f'Failed to execute query.'
            f'\nError: {e}'
            f'Traceback: {traceback.format_exc()}')
        return func.HttpResponse('Failed to execute query.', status_code=418)
