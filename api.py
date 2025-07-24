from flask import Flask, request, jsonify
import pmdarima
from pmdarima import auto_arima
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_percentage_error
import joblib
import contextlib
import os
 
app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process():
    try:
        data = request.json
        # print("Received Data:", data)  # Debugging print

        system_name = data.get('system', 'Guest')
        interval = data.get('interval', 5)
        dataset = data.get('dataset', [])
        # date_values = data.get('date_values', [])
        project_id = data.get('project_id', 777)

        df = pd.Series(dataset)
        forecast_interval = interval
        model_name = f"auto_arima_model_{project_id}"

        # print("Training ARIMA model...")
        arima_ml_model = auto_arima(df, seasonal=False, suppress_warnings=False)

        def run_arima_model():
            
            # Forecasting
            forecast_values = arima_ml_model.predict(n_periods=forecast_interval)
            
            train_size = int(len(dataset) * 0.4)
            train, test = dataset[:train_size], dataset[train_size:]

            if len(test) == 0:
                return {"error": "Test set is empty, cannot calculate accuracy"}

            # Naive forecast (last value of train)
            last_train_value = train[-1]
            naive_forecast = [last_train_value] * len(test)

            # MAPE Calculation
            mape = round(mean_absolute_percentage_error(test, naive_forecast) * 100, 2)
            accuracy = round(100 - mape, 2)

            return {
                "forecasts": forecast_values.tolist(),
                "accuracy": accuracy,
                "mape": mape,
                "model_type": "regression_model",
                "model_name": model_name
            }

        arima_model_data = run_arima_model()

        # Save the model
        save_folder = "models"
        os.makedirs(save_folder, exist_ok=True)
        file_path = os.path.join(save_folder, model_name + ".pkl")

        # print(f"Saving model to: {file_path}")
        with open(os.devnull, 'w'), contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
            joblib.dump(arima_ml_model, file_path)

        response = {
            "message": arima_model_data,
            "status": "saved"
        }

        # print("Response:", response)  # Debugging print
        return jsonify(response), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)