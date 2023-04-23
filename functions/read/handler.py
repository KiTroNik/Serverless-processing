import json

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

app = APIGatewayRestResolver()
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("facts")


@app.get("/facts/<fact_id>")
def get_fact_by_id(fact_id: str) -> dict:
    response = table.get_item(Key={"ID": fact_id})
    item = response["Item"]

    return {"fact": item}


def handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)
