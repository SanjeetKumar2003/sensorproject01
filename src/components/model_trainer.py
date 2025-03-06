import sys
import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from xgboost.sklearn import XGBClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from src.constant import *
from src.exception import CustomException
from src.logger import logging
from src.utils.main_utils import MainUtils
from dataclasses import dataclass

@dataclass
class ModelTrainerConfig:
    artifact_folder = os.path.join(artifact_folder)
    trained_model_path = os.path.join(artifact_folder, "model.pkl")
    expected_accuracy = 0.45  # Ensure consistency in threshold
    model_config_file_path = os.path.join('config', 'model.yaml')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.utils = MainUtils()
        self.models = {
            'XGBClassifier': XGBClassifier(),
            'GradientBoostingClassifier': GradientBoostingClassifier(),
            'SVC': SVC(),
            'RandomForestClassifier': RandomForestClassifier()
        }

    def evaluate_models(self, X_train, X_test, y_train, y_test, models):
        """Trains and evaluates multiple models."""
        try:
            report = {}
            for name, model in models.items():
                model.fit(X_train, y_train)  # Train model
                y_test_pred = model.predict(X_test)
                test_model_score = accuracy_score(y_test, y_test_pred)
                report[name] = test_model_score
            return report
        except Exception as e:
            raise CustomException(e, sys)

    def get_best_model(self, X_train, X_test, y_train, y_test):
        """Selects the best model based on test accuracy."""
        try:
            model_report = self.evaluate_models(X_train, X_test, y_train, y_test, self.models)
            logging.info(f"Model performance: {model_report}")

            best_model_name = max(model_report, key=model_report.get)
            best_model_score = model_report[best_model_name]
            best_model_object = self.models[best_model_name]

            return best_model_name, best_model_object, best_model_score
        except Exception as e:
            raise CustomException(e, sys)

    def finetune_best_model(self, best_model_name, best_model_object, X_train, y_train):
        """Fine-tunes the best model using GridSearchCV."""
        try:
            model_params = self.utils.read_yaml_file(self.model_trainer_config.model_config_file_path)["model_selection"]["model"]
            if best_model_name not in model_params:
                logging.warning(f"No hyperparameters found for {best_model_name}, using default model parameters.")
                return best_model_object

            param_grid = model_params[best_model_name]["search_param_grid"]
            grid_search = GridSearchCV(best_model_object, param_grid=param_grid, cv=5, n_jobs=-1, verbose=1)
            grid_search.fit(X_train, y_train)

            best_params = grid_search.best_params_
            logging.info(f"Best hyperparameters for {best_model_name}: {best_params}")
            return best_model_object.set_params(**best_params)
        except KeyError:
            logging.warning(f"Model {best_model_name} not found in configuration. Proceeding without fine-tuning.")
            return best_model_object
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_trainer(self, train_array, test_array):
        """Trains the best model and saves it."""
        try:
            logging.info("Splitting training and testing data")
            X_train, y_train = train_array[:, :-1], train_array[:, -1]
            X_test, y_test = test_array[:, :-1], test_array[:, -1]

            best_model_name, best_model, best_model_score = self.get_best_model(X_train, X_test, y_train, y_test)

            if best_model_score < self.model_trainer_config.expected_accuracy:
                raise Exception(f"No best model found with accuracy greater than {self.model_trainer_config.expected_accuracy}")

            best_model = self.finetune_best_model(best_model_name, best_model, X_train, y_train)
            best_model.fit(X_train, y_train)

            y_pred = best_model.predict(X_test)
            final_model_score = accuracy_score(y_test, y_pred)
            logging.info(f"Final trained model: {best_model_name} with accuracy: {final_model_score}")

            os.makedirs(os.path.dirname(self.model_trainer_config.trained_model_path), exist_ok=True)
            self.utils.save_object(self.model_trainer_config.trained_model_path, best_model)

            return self.model_trainer_config.trained_model_path
        except Exception as e:
            raise CustomException(e, sys)
