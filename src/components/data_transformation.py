import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
from dataclasses import dataclass

from src.constant import *  # Ensure TARGET_COLUMN and artifact_folder are defined
from src.exception import CustomException
from src.logger import logging
from src.utils.main_utils import MainUtils


@dataclass
class DataTransformationConfig:
    artifact_dir = os.path.join(artifact_folder)
    transformed_train_file_path = os.path.join(artifact_dir, 'train.npy')
    transformed_test_file_path = os.path.join(artifact_dir, 'test.npy')
    transformed_object_file_path = os.path.join(artifact_dir, 'preprocessor.pkl')


class DataTransformation:
    def __init__(self, feature_store_file_path: str):
        self.feature_store_file_path = feature_store_file_path
        self.data_transformation_config = DataTransformationConfig()
        self.utils = MainUtils()

    @staticmethod
    def get_data(feature_store_file_path: str) -> pd.DataFrame:
        """
        Reads data from the feature store file path and renames the target column.
        """
        try:
            data = pd.read_csv(feature_store_file_path)

            # Ensure the "Good/Bad" column exists before renaming
            if "Good/Bad" not in data.columns:
                raise ValueError(f"'Good/Bad' column not found in dataset: {feature_store_file_path}")

            data.rename(columns={"Good/Bad": TARGET_COLUMN}, inplace=True)

            return data
        except Exception as e:
            raise CustomException(e, sys)

    def get_data_transformer_object(self) -> Pipeline:
        """
        Creates a preprocessing pipeline with imputation and scaling.
        """
        try:
            preprocessor = Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
                ('scaler', RobustScaler())
            ])
            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self):
        """
        Handles data transformation, including preprocessing and saving the preprocessor object.
        """
        logging.info("Entered initiate_data_transformation method of DataTransformation class")

        try:
            dataframe = self.get_data(feature_store_file_path=self.feature_store_file_path)

            # Ensure the target column exists
            if TARGET_COLUMN not in dataframe.columns:
                raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset.")

            X = dataframe.drop(columns=[TARGET_COLUMN])
            y = np.where(dataframe[TARGET_COLUMN] == -1, 0, 1)  # Converting target labels

            # Train-test split with fixed random state
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            preprocessor = self.get_data_transformer_object()

            # Transforming data
            X_train_scaled = preprocessor.fit_transform(X_train)
            X_test_scaled = preprocessor.transform(X_test)

            # Save preprocessor object
            preprocessor_path = self.data_transformation_config.transformed_object_file_path
            os.makedirs(os.path.dirname(preprocessor_path), exist_ok=True)
            self.utils.save_object(file_path=preprocessor_path, obj=preprocessor)

            # Storing transformed arrays
            train_arr = np.c_[X_train_scaled, y_train]
            test_arr = np.c_[X_test_scaled, y_test]

            logging.info("Successfully transformed data and saved preprocessor.")

            return train_arr, test_arr, preprocessor_path

        except Exception as e:
            raise CustomException(e, sys) from e
