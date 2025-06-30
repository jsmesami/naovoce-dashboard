import boto3


def get_bucket(current_app):
    session = boto3.Session(
        aws_access_key_id=current_app.config.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=current_app.config.get("AWS_SECRET_ACCESS_KEY"),
    )
    s3 = session.resource("s3")
    return s3.Bucket(current_app.config.get("S3_BUCKET_NAME"))
