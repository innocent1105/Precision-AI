from flask import Flask, request, jsonify
from prophet import Prophet
import pandas as pd
import json
import os
import joblib
import contextlib
from sklearn.metrics import mean_absolute_percentage_error

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process():
    try:
        data = request.json

        system_name = data.get('system', 'Guest')
        interval = data.get('interval', 5)  # how many steps to forecast
        dataset = data.get('dataset', [])   # list of values
        date_values = data.get('date_values', [])  # matching date strings like ['2011', '2012', ...]
        project_id = data.get('project_id', 777)

        if len(dataset) != len(date_values):
            return jsonify({"error": "Length of dataset and date_values must be equal"}), 400

        # Convert to DataFrame
        df = pd.DataFrame({
            'ds': pd.to_datetime(date_values),  # Converts years like "2011" to "2011-01-01"
            'y': dataset
        })

        # Train Prophet model
        model = Prophet()
        model.fit(df)

        # Forecast future
        future = model.make_future_dataframe(periods=interval, freq='Y')  # yearly forecast
        forecast = model.predict(future)

        # Get only future forecasted values
        future_forecast = forecast[forecast['ds'] > df['ds'].max()]
        forecast_values = future_forecast[['ds', 'yhat']].to_dict(orient='records')

        # Accuracy using naive approach for reference (not Prophet)
        train_size = int(len(dataset) * 0.4)
        train, test = dataset[:train_size], dataset[train_size:]

        if len(test) > 0:
            last_train_value = train[-1]
            naive_forecast = [last_train_value] * len(test)
            mape = round(mean_absolute_percentage_error(test, naive_forecast) * 100, 2)
            accuracy = round(100 - mape, 2)
        else:
            mape = None
            accuracy = None

        # Save model
        save_folder = "models"
        os.makedirs(save_folder, exist_ok=True)
        model_name = f"prophet_model_{project_id}"
        file_path = os.path.join(save_folder, model_name + ".pkl")
        with open(os.devnull, 'w'), contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
            joblib.dump(model, file_path)

        return jsonify({
            "message": {
                "forecasts": forecast_values,
                "accuracy": accuracy,
                "mape": mape,
                "model_type": "prophet_model",
                "model_name": model_name
            },
            "status": "saved"
        }), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
