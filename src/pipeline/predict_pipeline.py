import os
import sys
import pandas as pd
from flask import request
from dataclasses import dataclass

from src.logger import logging
from src.exception import CustomException
from src.constant import *
from src.utils.main_utils import MainUtils


@dataclass
class PredictionPipelineConfig:
    prediction_output_dirname: str = "predictions"
    prediction_file_name: str = "prediction_file.csv"
    model_file_path: str = os.path.join(artifact_folder, 'model.pkl')
    preprocessor_path: str = os.path.join(artifact_folder, 'preprocessor.pkl')
    prediction_file_path: str = os.path.join(prediction_output_dirname, prediction_file_name)


class PredictionPipeline:
    def __init__(self, request: request):
        self.request = request
        self.utils = MainUtils()
        self.prediction_pipeline_config = PredictionPipelineConfig()

    def save_input_files(self) -> str:
        """Save the uploaded CSV file and return its file path."""
        try:
            pred_file_input_dir = "prediction_artifacts"
            os.makedirs(pred_file_input_dir, exist_ok=True)

            # ✅ Check if file is in request
            if 'file' not in self.request.files:
                raise CustomException("No file uploaded. Please upload a valid CSV file.", sys)

            input_csv_file = self.request.files['file']

            # ✅ Check if the uploaded file is not empty
            if input_csv_file.filename == '':
                raise CustomException("No selected file. Please select a CSV file to upload.", sys)

            # ✅ Save file
            pred_file_path = os.path.join(pred_file_input_dir, input_csv_file.filename)
            input_csv_file.save(pred_file_path)

            logging.info(f"File saved successfully at: {pred_file_path}")
            return pred_file_path

        except Exception as e:
            raise CustomException(f"Error saving input file: {e}", sys)

    def load_model_objects(self):
        """Load trained model and preprocessor."""
        try:
            if not os.path.exists(self.prediction_pipeline_config.model_file_path):
                raise CustomException(f"Model file not found at {self.prediction_pipeline_config.model_file_path}", sys)

            if not os.path.exists(self.prediction_pipeline_config.preprocessor_path):
                raise CustomException(f"Preprocessor file not found at {self.prediction_pipeline_config.preprocessor_path}", sys)

            model = self.utils.load_object(self.prediction_pipeline_config.model_file_path)
            preprocessor = self.utils.load_object(self.prediction_pipeline_config.preprocessor_path)

            return model, preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, features):
        """Preprocess input data and make predictions."""
        try:
            model, preprocessor = self.load_model_objects()
            transformed_x = preprocessor.transform(features)
            preds = model.predict(transformed_x)

            return preds
        except Exception as e:
            raise CustomException(e, sys)

    def get_predicted_dataframe(self, input_dataframe_path: str):
        """Load input CSV, make predictions, and save the results."""
        try:
            prediction_column_name = TARGET_COLUMN
            input_dataframe = pd.read_csv(input_dataframe_path)

            if "Unnamed: 0" in input_dataframe.columns:
                input_dataframe = input_dataframe.drop(columns=["Unnamed: 0"])

            predictions = self.predict(input_dataframe)
            input_dataframe[prediction_column_name] = predictions

            target_column_mapping = {0: 'bad', 1: 'good'}
            input_dataframe[prediction_column_name] = input_dataframe[prediction_column_name].map(target_column_mapping)

            # Ensure the output directory exists
            os.makedirs(self.prediction_pipeline_config.prediction_output_dirname, exist_ok=True)

            # Save predictions
            input_dataframe.to_csv(self.prediction_pipeline_config.prediction_file_path, index=False)

            logging.info(f"Predictions saved successfully at: {self.prediction_pipeline_config.prediction_file_path}")

        except Exception as e:
            raise CustomException(e, sys)

    def run_pipeline(self):
        """Run the complete prediction pipeline."""
        try:
            input_csv_path = self.save_input_files()
            self.get_predicted_dataframe(input_csv_path)

            return self.prediction_pipeline_config
        except Exception as e:
            raise CustomException(e, sys)
