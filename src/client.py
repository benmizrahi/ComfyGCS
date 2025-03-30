import os
import logging
from google.cloud import storage

from dotenv import load_dotenv

class GoogleStorageClient:
    _instance = None  # Class-level attribute to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GoogleStorageClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, bucket_name=None):
        """
        Initialize the Google Storage Client.
        :param bucket_name: Name of the Google Cloud Storage bucket.
        """
        if not hasattr(self, 'initialized'):  # Ensure __init__ runs only once
            load_dotenv()
            sa_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not sa_file:
                logging.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set USING ADC.")
            self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
            if not self.bucket_name:
                raise ValueError("GCS_BUCKET_NAME environment variable is not set.")

            self.client = storage.Client(credentials=sa_file)
            self.bucket = self.client.bucket(bucket_name)
            self.initialized = True

    def download_file(self, gcs_path, local_path):
        """
        Downloads a file from Google Cloud Storage to a local path.
        :param gcs_path: Path of the file in Google Cloud Storage.
        :param local_path: Local path to save the downloaded file.
        """
        blob = self.bucket.blob(gcs_path)
        blob.download_to_filename(local_path)
        print(f"Downloaded {gcs_path} to {local_path}")

    def get_save_path(self, filename_prefix, width, height):
        """
        Generates a save path for the image.
        :param filename_prefix: Prefix for the filename.
        :param width: Width of the image.
        :param height: Height of the image.
        :return: Tuple containing full output folder, filename, counter, subfolder, and filename prefix.
        """
        # Implement logic to generate save path
        # This is a placeholder implementation
        full_output_folder = os.path.join(self.bucket_name, "output")
        filename = f"{filename_prefix}_{width}x{height}"
        counter = 0
        subfolder = ""
        return full_output_folder, filename, counter, subfolder, filename_prefix

    def list_files(self, prefix=None):
        """
        Lists all the files in the bucket with the given prefix.
        :param prefix: Prefix to filter the files.
        :return: List of file names.
        """
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]

    