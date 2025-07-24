from flask import Flask, request, jsonify
import joblib
import os
import numpy as np

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def process():
    data = request.json
    model_name = data.get("model_name", "none")
    forecast_interval = data.get("interval")

    model_name = model_name + ".pkl"
    model_path = os.path.join("models", model_name)

    try:
        # Load model
        loaded_model = joblib.load(model_path)
        
        # Generate forecast
        forecast = loaded_model.predict(n_periods=forecast_interval)

        response = {"forecast": forecast.tolist()}
        return jsonify(response), 200

    except FileNotFoundError:
        return jsonify({"error": f"Model file '{model_name}.pkl' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
