"""Publish validated Athena UNLOAD data to a deterministic curated S3 partition.

Derived from the corrected sales-publisher Lambda saved during project development.
Requires SALES_BUCKET in the Lambda environment and scoped S3 IAM permissions.
This function copies data only; Glue partition registration is orchestrated separately.
"""
import os
import re

import boto3

s3 = boto3.client("s3")
# Fail closed if the deployment has not supplied its private bucket.
BUCKET = os.environ["SALES_BUCKET"]


def lambda_handler(event, context):
    """Copy one validated batch and return its curated S3 prefix."""
    batch_id = event["batchId"]
    # The batch ID is used in S3 key paths: reject unexpected characters.
    if not isinstance(batch_id, str) or not re.fullmatch(r"[a-f0-9]{64}", batch_id):
        raise ValueError("Invalid batchId")

    src_prefix = f"automated/validation/{batch_id}/"
    dst_prefix = f"automated/curated/sales/batch_id={batch_id}/"
    objects = []

    # Athena UNLOAD may create Parquet data objects without a .parquet suffix.
    # The validation prefix must contain only this batch's UNLOAD output.
    for page in s3.get_paginator("list_objects_v2").paginate(
        Bucket=BUCKET, Prefix=src_prefix
    ):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if (
                obj["Size"] > 0
                and not key.endswith("/")
                and not key.endswith("_SUCCESS")
                and not key.endswith(".metadata")
                and not key.endswith(".crc")
            ):
                objects.append(obj)

    # Do not publish an empty or missing validation batch.
    if not objects:
        raise ValueError("No Parquet data objects found for batch")

    for obj in objects:
        source_key = obj["Key"]
        target_key = dst_prefix + source_key[len(src_prefix):]
        # Deterministic destination keys make a repeat copy overwrite the
        # same objects instead of creating a new set of keys.
        s3.copy_object(
            Bucket=BUCKET,
            Key=target_key,
            CopySource={"Bucket": BUCKET, "Key": source_key},
            MetadataDirective="COPY",
        )
        # Compare object sizes as a lightweight post-copy sanity check.
        # Size equality alone is NOT an end-to-end content-integrity proof.
        head = s3.head_object(Bucket=BUCKET, Key=target_key)
        if head["ContentLength"] != obj["Size"]:
            raise RuntimeError("Copied object size mismatch")

    return {
        "batchId": batch_id,
        "curatedPrefix": f"s3://{BUCKET}/{dst_prefix}",
        "publishedObjectCount": len(objects),
    }
