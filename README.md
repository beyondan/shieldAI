# REST APIs

- Base URL: https://shieldai-apim.azure-api.net/shieldaifunctionapp
- For all requests, include the following in the header
```json
{"Ocp-Apim-Subscription-Key": "86f2bdb199a24578928aec54f3c4b4c6"}
```
- Recommend using Postman to make API requests. Import my Postman requests collection file in 'testfiles' folder.

# POST /GetQueryResult
Executes a Kusto query. 

[Kusto Query Language (KQL) Overview](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/)

Example body (JSON):
```json
{
    "query": "FlightEvents | count"
}
```
Example response:
```json
{"Count":{"0":42260}}
```

# POST /InsertFlightData
Inserts one or more rows of flight data into the database.

Example body (JSON):
```json
{
    "data": [
        ["V-BAT", "1", "2021-01-01T00:00:00.000000", "2021-01-01T00:00:30.000000", "xn76m27ty9g4"],
        ["V-BAT", "2", "2021-01-01T00:00:30.000000", "2021-01-01T00:01:00.000000", "xn76m27ty9g5"],
        ...
    ]
}
```
Example response:
```
Successfully queued all flight data for ingestion.
```

# POST /InsertFlightDataBulk
Inserts a csv file containing flight data into the database.

Example body (form-data):
```
"file=@my_data_file.csv"
```
Example response:
```
Successfully queued all files for ingestion. Result: None
```