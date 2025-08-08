import os
from pathlib import Path
import pandas as pd
import boto3
from botocore.exceptions import ClientError


def list_s3_files(bucket: str) -> list[str]:
    """
    Lists all object keys (files) in an S3 bucket.

    :param bucket: The name of the S3 bucket.
    :return: A list of file names (keys).
    :raises ClientError: If the bucket does not exist or permissions are denied.
    """
    s3 = boto3.client('s3')
    file_list = []
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket)
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                file_list.append(obj['Key'])
    return file_list

def upload_s3_file(bucket: str,
                   s3_path: str | None = None,
                   local_path: str | None = None) -> bool:
    """
    Uploads a file to an S3 bucket.

    :param local_path: The path to the local file to upload.
    :param bucket: The destination S3 bucket.
    :param s3_path: The destination path (key) in S3. If None, the local filename is used.
    :return: True if the upload was successful, False otherwise.
    """
    if s3_path is None:
        s3_path = os.path.basename(local_path)
    
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(local_path, bucket, s3_path)
    except (ClientError, FileNotFoundError) as e:
        print(f"❌ Error uploading file: {e}")
        return False
    return True

def _read_file_to_df(file_path: str, low_memory: bool = True, sep: str | None = ',') -> pd.DataFrame:
    """Helper function to read a file into a Pandas DataFrame."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path, low_memory=low_memory, sep=sep)
    if file_path.endswith(".dta"):
        # Requires the 'pyreadstat' package
        return pd.read_stata(file_path)
    raise ValueError(f"Unsupported file format for DataFrame: {file_path}")

def download_s3_file(
        bucket: str,
        s3_path: str,
        local_path: str | None = None,
        to_df: bool = False,
        low_memory: bool = True,
        replace: bool = False,
        sep: str = ','
) -> pd.DataFrame | str:
    """
    Downloads a file from S3, defaulting to a 'data/' subdirectory.

    :param bucket: The name of the S3 bucket.
    :param s3_path: The path (key) of the file within the bucket.
    :param local_path: Optional. The local path to save the file.
                       If not provided, defaults to 'data/[original_filename]'.
    :param to_df: If True, returns a Pandas DataFrame.
    :return: A Pandas DataFrame or the path to the local file.
    """
    # If no local_path is given, create a default one.
    if local_path is None:
        filename = os.path.basename(s3_path)
        local_path = f"data/{filename}"

    path_obj = Path(local_path)
    if not replace and path_obj.exists():
        # If the file exists and replace is False, skip download.
        print(f"ℹ️ File already exists at '{local_path}'. Skipping download.")
        if to_df:
            return _read_file_to_df(str(path_obj), low_memory=low_memory, sep=sep)
        return str(path_obj)
    
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client('s3')
    try:
        print(f"⬇️ Downloading file from S3: {s3_path}")
        s3.download_file(bucket, s3_path, str(path_obj))            
        print("✅ Download complete.")
    except ClientError as e:
        print(f"❌ Error during download: {e}")
        raise

    if to_df:
        return _read_file_to_df(str(path_obj), low_memory=low_memory, sep=sep)
    return str(path_obj)