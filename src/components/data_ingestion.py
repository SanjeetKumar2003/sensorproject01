import sys
import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from pathlib import Path  # Correcting import
from src.constant import *
from src.exception import CustomException
from src.logger import logging
from src.utils.main_utils import MainUtils
from dataclasses import dataclass


@dataclass
class DataIngestionConfig:
    artifact_folder: str = os.path.join(artifact_folder)  # Ensure artifact_folder is correctly defined in src.constant


class DataIngestion:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.utils = MainUtils()

    def export_collection_as_dataframe(self, collection_name: str, db_name: str) -> pd.DataFrame:
        """
        Exports a MongoDB collection as a Pandas DataFrame.
        """
        try:
            mongo_client = MongoClient(MONGO_DB_URL)  # Ensure MONGO_DB_URL is defined
            collection = mongo_client[db_name][collection_name]

            df = pd.DataFrame(list(collection.find()))

            if "_id" in df.columns:
                df = df.drop(columns=['_id'])

            df.replace({"na": np.nan}, inplace=True)

            return df
        except Exception as e:
            raise CustomException(e, sys)

    def export_data_into_feature_store_file_path(self) -> str:
        """
        Fetches data from MongoDB and stores it as a CSV file.
        """
        try:
            logging.info("Exporting data from MongoDB...")
            raw_file_path = self.data_ingestion_config.artifact_folder

            os.makedirs(raw_file_path, exist_ok=True)

            sensor_data = self.export_collection_as_dataframe(
                collection_name=MONGO_COLLECTION_NAME,
                db_name=MONGO_DATABASE_NAME
            )

            feature_store_file_path = os.path.join(raw_file_path, 'wafer_fault.csv')

            logging.info(f"Saving exported data to {feature_store_file_path}")
            sensor_data.to_csv(feature_store_file_path, index=False)

            return feature_store_file_path
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_ingestion(self) -> str:
        """
        Initiates the data ingestion process.
        """
        logging.info("Entered initiate_data_ingestion method of DataIngestion class")

        try:
            feature_store_file_path = self.export_data_into_feature_store_file_path()

            logging.info("Successfully exported data from MongoDB")
            logging.info("Exited initiate_data_ingestion method of DataIngestion class")

            return feature_store_file_path
        except Exception as e:
            raise CustomException(e, sys)
