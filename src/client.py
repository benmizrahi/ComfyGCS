import os
import logging
import google.auth
from google.cloud import storage
from dotenv import load_dotenv


class GoogleStorageClient:
    _instance = None  # Class-level attribute to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GoogleStorageClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, bucket_name=None, project=None, credentials_sa=None):
        """
        Initialize the Google Storage Client.
        :param bucket_name: Name of the Google Cloud Storage bucket.
        """
        if not hasattr(self, 'initialized'):  # Ensure __init__ runs only once
            logging.info("Initializing Google Storage Client")
            load_dotenv()
            credentials = None
            if credentials_sa:
                logging.info(f"Using service account credentials from: {credentials_sa}")
                credentials = google.auth.load_credentials_from_file(credentials_sa)
            self.client = storage.Client(project=project)
            self.bucket_name = bucket_name
            self.bucket = self.client.bucket(bucket_name)
            logging.info(f"Google Storage Client initialized with bucket: {bucket_name}")
            self.initialized = True
            self.last_input_values = None  # Store the last input values to detect changes

    def download_file(self, gcs_path, local_path):
        """
        Downloads a file from Google Cloud Storage to a local path.
        :param gcs_path: Path of the file in Google Cloud Storage.
        :param local_path: Local path to save the downloaded file.
        """
        logging.info(f"Downloading {gcs_path} to {local_path}")
        blob = self.bucket.blob(gcs_path)
        blob.download_to_filename(local_path)
        logging.info(f"Downloaded {gcs_path} to {local_path}")
        return local_path

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
        logging.info(f"Generating save path for {filename_prefix} with dimensions {width}x{height}")
        filename = f"{filename_prefix}_{width}x{height}"
        counter = 0
        subfolder = ""
        return "output", filename, counter, subfolder, filename_prefix

    def list_files(self, prefix=None):
        """
        Lists all the files in the bucket with the given prefix.
        :param prefix: Prefix to filter the files.
        :return: List of file names.
        """
        logging.info(f"Listing files in bucket: {self.bucket_name} with prefix: {prefix}")
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]

    def monitor_input_and_list_files(self, input_values):
        """
        Monitors changes in input values and triggers the list_files method if changes are detected.
        :param input_values: Dictionary of input values to monitor.
        """
        if input_values != self.last_input_values:
            logging.info("Input values changed, triggering list_files.")
            self.last_input_values = input_values
            prefix = input_values.get("prefix", None)
            return self.list_files(prefix=prefix)
        else:
            logging.info("No changes in input values detected.")
            return []

    def handle_input_change(self, new_inputs):
        """
        Handles changes in required inputs and triggers file listing.
        :param new_inputs: Dictionary of new input values.
        """
        logging.info("Handling input change.")
        return self.monitor_input_and_list_files(new_inputs)

    def upload_file(self, local_path, gcs_path):
        """
        Uploads a file from local path to Google Cloud Storage.
        :param local_path: Local path of the file to upload.
        :param gcs_path: Path in Google Cloud Storage where the file will be uploaded.
        """
        logging.info(f"Uploading {local_path} to {gcs_path}")
        blob = self.bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        logging.info(f"Uploaded {local_path} to {gcs_path}")
        return gcs_path
