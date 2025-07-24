from flask import Flask, request, jsonify
from prophet import Prophet
import joblib
import pandas as pd
import os

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse incoming JSON
        data = request.get_json()
        model_name = data.get("model_name")
        periods = int(data.get("interval", 5))  # Default to 5 if not provided

        if not model_name:
            return jsonify({"error": "Model name is required."}), 400

        # Build full model path
        model_path = os.path.join("models", model_name)

        if not os.path.exists(model_path):
            return jsonify({"error": f"Model '{model_name}' not found."}), 404

        # Load model using joblib
        model = joblib.load(model_path)

        # Make future dataframe and predict
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        # Prepare and return only the forecasted part
        result = forecast[['ds', 'yhat']].tail(periods).to_dict(orient="records")
        return jsonify({"forecast": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=7070, debug=True)
