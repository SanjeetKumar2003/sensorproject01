import sys
import os
import pickle
import yaml
import pandas as pd
import boto3  # Keeping this for future S3 functionality

from src.constant import *
from src.exception import CustomException
from src.logger import logging


class MainUtils:
    def __init__(self) -> None:
        pass

    def read_yaml_file(self, filename: str) -> dict:
        """
        Reads a YAML file and returns its content as a dictionary.
        """
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"YAML file not found: {filename}")

            with open(filename, "r") as yaml_file:
                return yaml.safe_load(yaml_file)

        except Exception as e:
            logging.error(f"Error reading YAML file: {filename}")
            raise CustomException(e, sys) from e

    def read_schema_config_file(self) -> dict:
        """
        Reads the schema configuration file and returns its contents.
        """
        try:
            schema_config_path = os.path.join("config", "schema.yaml")

            if not os.path.exists(schema_config_path):
                raise FileNotFoundError(f"Schema config file not found: {schema_config_path}")

            return self.read_yaml_file(schema_config_path)

        except Exception as e:
            logging.error("Error reading schema configuration file")
            raise CustomException(e, sys) from e

    @staticmethod
    def save_object(file_path: str, obj: object) -> None:
        """
        Saves an object using pickle.
        """
        try:
            dir_name = os.path.dirname(file_path)
            if dir_name:  # Prevents issue if no directory is provided
                os.makedirs(dir_name, exist_ok=True)

            with open(file_path, "wb") as file_obj:
                pickle.dump(obj, file_obj)

            logging.info(f"Object successfully saved to {file_path}")

        except Exception as e:
            logging.error(f"Error saving object to {file_path}")
            raise CustomException(e, sys) from e

    @staticmethod
    def load_object(file_path: str) -> object:
        """
        Loads an object from a pickle file.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Pickle file not found: {file_path}")

            with open(file_path, "rb") as file_obj:
                obj = pickle.load(file_obj)

            logging.info(f"Object successfully loaded from {file_path}")

            return obj

        except Exception as e:
            logging.error(f"Error loading object from {file_path}")
            raise CustomException(e, sys) from e

    def upload_file_to_s3(self, file_name: str, bucket: str, object_name: str = None):
        """
        Uploads a file to an S3 bucket.
        """
        try:
            s3_client = boto3.client('s3')
            if object_name is None:
                object_name = os.path.basename(file_name)

            s3_client.upload_file(file_name, bucket, object_name)
            logging.info(f"File {file_name} uploaded to S3 bucket {bucket} as {object_name}")

        except Exception as e:
            logging.error(f"Error uploading {file_name} to S3 bucket {bucket}")
            raise CustomException(e, sys) from e

    def download_file_from_s3(self, bucket: str, object_name: str, file_name: str):
        """
        Downloads a file from an S3 bucket.
        """
        try:
            s3_client = boto3.client('s3')
            s3_client.download_file(bucket, object_name, file_name)
            logging.info(f"File {object_name} downloaded from S3 bucket {bucket} to {file_name}")

        except Exception as e:
            logging.error(f"Error downloading {object_name} from S3 bucket {bucket}")
            raise CustomException(e, sys) from e
