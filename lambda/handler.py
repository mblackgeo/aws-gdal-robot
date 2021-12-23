import json
import os
import urllib.parse
from datetime import datetime

import boto3


def main(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    print(f"Submitting batch job to convert : {bucket}{key}")

    job_defn = os.environ["BATCH_JOB_DEFINITION"]
    job_queue = os.environ["BATCH_JOB_QUEUE"]

    print(f"Using batch job defn : {job_defn}")
    print(f"Using batch job queue : {job_queue}")

    # submit the s3 bucket and key to the AWS Batch job queue
    response = boto3.client("batch").submit_job(
        jobName=f"convert-{bucket}-{key}-{int(datetime.utcnow().timestamp())}",
        jobDefinition=job_defn,
        jobQueue=job_queue,
        containerOverrides={
            "environment": [
                {
                    "name": "INPUT_BUCKET",
                    "value": bucket,
                },
                {
                    "name": "INPUT_KEY",
                    "value": key,
                },
            ]
        },
    )

    print(response)
    return {"statusCode": 200}
