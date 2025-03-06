from flask import Flask, render_template, jsonify, request, send_file
from src.exception import CustomException
from src.logger import logging as lg
import os, sys

from src.pipeline.train_pipeline import TrainingPipeline
from src.pipeline.predict_pipeline import PredictionPipeline

app = Flask(__name__)

# Ensure `src` directory is in the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

@app.route("/")
def home():
    lg.info("Home route accessed")
    return "Welcome to my application"

@app.route("/train")
def train_route():
    try:
        lg.info("Training route initiated.")
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        lg.info("Training completed successfully.")
        return jsonify({"message": "Training Completed."})
    except Exception as e:
        lg.error(f"Error in training: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST', 'GET'])
def upload():
    try:
        if request.method == 'POST':
            lg.info("Prediction request received.")

            if 'file' not in request.files:
                return jsonify({"error": "No file part in request"}), 400

            # Initialize prediction pipeline with request object
            prediction_pipeline = PredictionPipeline(request)
            prediction_file_detail = prediction_pipeline.run_pipeline()

            lg.info(f"Prediction completed. Downloading {prediction_file_detail.prediction_file_name}")
            return send_file(
                prediction_file_detail.prediction_file_path,
                download_name=prediction_file_detail.prediction_file_name,
                as_attachment=True
            )
        else:
            return render_template('upload_file.html')
    except Exception as e:
        lg.error(f"Error in prediction: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    lg.info("Starting Flask Application")
    app.run(host="0.0.0.0", port=5000, debug=True)
