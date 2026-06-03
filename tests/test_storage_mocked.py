import boto3
from moto import mock_aws


@mock_aws
def test_s3_upload_with_moto(temp_dir):
    """Test S3 upload using moto mock."""
    # Create mock S3 bucket
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket="test-bucket")

    # Create test file
    test_file = temp_dir / "test.csv"
    test_file.write_text("test,data")

    # Verify mock works
    s3_object = conn.Object("test-bucket", "test.csv")
    s3_object.put(Body=b"test,data")

    # Check it was stored
    assert s3_object.get()["Body"].read() == b"test,data"
