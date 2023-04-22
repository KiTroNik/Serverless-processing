import io
import csv

import boto3
import requests
from requests import Response
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

s3 = boto3.client("s3")
app = APIGatewayRestResolver()


@app.post("/process_fact")
def fetch_for_processing():
    request_data: dict = app.current_event.json_body

    fact: Response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    fact.raise_for_status()
    request_data["fact"] = fact.json()["text"]

    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=["fact", "email"])
    writer.writeheader()
    writer.writerow(request_data)
    csv_string_object = stream.getvalue()
    s3.put_object(Bucket="bucket_name", Key=f"{fact.json()['id']}.csv", Body=csv_string_object)

    return {
        "fact": fact.json(),
        "email": request_data["email"]
    }


def _fetch_fact() -> Response:
    result: Response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    result.raise_for_status()
    return result


def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
