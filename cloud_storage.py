from google.cloud import storage


def upload_to_gcs(bucket_name, file_path):
    """Upload a file to Google Cloud Storage."""
    # Create a client object
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the file to the bucket
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)
