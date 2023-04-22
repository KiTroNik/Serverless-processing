import csv
import io

import boto3
import requests
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from requests import Response

s3 = boto3.client("s3")
app = APIGatewayRestResolver()


@app.post("/process_fact")
def fetch_for_processing():
    request_data: dict = app.current_event.json_body
    fact = _fetch_fact()
    request_data["fact"] = fact.json()["text"]

    csv_string_object = _create_csv_from_dict(request_data)
    file_name = f"{fact.json()['id']}.csv"

    s3.put_object(Bucket="bucket_name", Key=file_name, Body=csv_string_object)

    return {"fact": fact.json(), "email": request_data["email"]}


def _fetch_fact() -> Response:
    result: Response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    result.raise_for_status()
    return result


def _create_csv_from_dict(dict_to_process: dict) -> str:
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(dict_to_process.keys()))
    writer.writeheader()
    writer.writerow(dict_to_process)
    return stream.getvalue()


def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
