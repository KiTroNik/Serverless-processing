import csv
import json
import uuid

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("facts")
ses = boto3.client("ses", region_name="us-east-1")


def handler(event: dict, context: LambdaContext) -> dict:
    for record in event["Records"]:
        payload = record["body"]

        if payload.get("Event", None) == "s3:TestEvent":
            return {
                "statusCode": 200,
                "body": json.dumps("Test event detected. Ignoring."),
            }

        payload = payload["Records"][0]

        bucket_name = payload["s3"]["bucket"]["name"]
        object_name = payload["s3"]["object"]["key"]

        fact_to_process = _download_file_from_s3(bucket_name, object_name)
        processed_fact = _process_the_data(fact_to_process)
        item_id = _write_data_to_dynamodb(processed_fact)
        message_id = _send_user_ses_email(processed_fact["email"], item_id)

        return {
            "statusCode": 200,
            "body": json.dumps(
                f"Data processed successfully. ID has been sent to user email. Id of message {message_id}"
            ),
        }


def _download_file_from_s3(bucket_name: str, object_name: str) -> dict:
    file = (
        s3.get_object(Bucket=bucket_name, Key=object_name)["Body"]
        .read()
        .decode("utf-8")
    )
    reader = csv.DictReader(file.splitlines())
    return [row for row in reader][0]  # type: ignore


def _process_the_data(data: dict) -> dict:
    for el in data:
        if el != "email":
            data[el] = data[el].upper()
    return data


def _write_data_to_dynamodb(data: dict) -> str:
    unique_id = str(uuid.uuid4())
    response = table.put_item(Item={"ID": unique_id, "fact": data["fact"]})
    print(response)  # log for CloudWatch
    return unique_id


def _send_user_ses_email(user_email: str, item_id: str):
    response = ses.send_email(
        Destination={"ToAddresses": [user_email]},
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": f"You can access processed data by id {item_id}",
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "Your request has been proccessed succesfully.",
            },
        },
        Source="SourceEmailAddress",  # todo: Change it to your verified SES identity
    )
    return response["MessageId"]
