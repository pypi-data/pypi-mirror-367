import os
import time
import logging
from pathlib import Path
from pprint import pprint
from eo4eu_data_utils.stream import S3Driver

logger = logging.getLogger("test")
logging.basicConfig()
logger.setLevel(logging.DEBUG)


boto_config = {
    "region_name": "us-east-1",
    "endpoint_url": os.environ["S3_ENDPOINT_URL"],
    "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
    "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
}

def test_summary():
    s3_driver = S3Driver(
        config = boto_config,
        bucket = "test_pre_pro-base"
    )

    # for obj in s3_driver.list_objects("source"):
    #     print(obj.key)
    #     print(obj.size, s3_driver.get_object_summary(obj.key).size)

    objs = s3_driver.list_objects()
    keys = [obj.key for obj in objs]
    summaries = s3_driver.get_object_summaries(keys)
    # pprint(objs)
    # pprint(summaries)

    for obj, summary in zip(objs, summaries):
        # print(obj.key, summary.key)
        # print(obj.size, summary.size)
        assert obj.key == summary.key
        assert obj.size == summary.size
    # for obj in objs:
    #     for summary in summaries:
    #         if obj.key == summary.key:
    #             print(obj.key, summary.key)
    #             print(obj.size, summary.size)


def test_basic():
    s3_driver = S3Driver(
        config = boto_config,
        bucket = "test_pre_pro-base"
        # bucket = "faas-kostas"
    )
    # s3_driver_insitu = S3Driver(
    #     config = boto_config,
    #     bucket = "eo4eu-insitu"
    # )

    for obj in s3_driver.list_objects():
        print(obj.key)

    for obj in s3_driver.list_objects("source/"):
        print(obj.key)

    s3_driver.download_file("source/INSITU/Bands.csv", "out/bands.csv")

    for item in s3_driver.bucket.objects.filter(Prefix = "faas_output"):
        print(item.key, item.last_modified)


def test_bucket_create():
    s3_driver = S3Driver(
        config = boto_config,
        bucket = "nonexistent-bucket"
    )

    s3_driver.upload_file("input/archive0.zip", "some/path/to/archive0.zip")


if __name__ == "__main__":
    # test_basic()
    # test_bucket_create()
    test_summary()
