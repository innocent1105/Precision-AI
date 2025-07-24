from flask import Flask, request, jsonify
from prophet import Prophet
import pandas as pd
import json
import os
import joblib
import contextlib
from sklearn.metrics import mean_absolute_percentage_error
from datetime import datetime

app = Flask(__name__)

# 🔧 Clean & convert date values to proper datetimes
from datetime import datetime
import pandas as pd

def clean_and_prepare_for_prophet(ds_raw, y_raw):
    cleaned_ds = []

    for val in ds_raw:
        try:
            # Case 1: Already a datetime object
            if isinstance(val, pd.Timestamp) or isinstance(val, datetime):
                cleaned_ds.append(val)
                continue

            val_str = str(val).strip()

            # Case 2: Blank or NaN
            if val_str == '' or pd.isna(val):
                cleaned_ds.append(None)
                continue

            # Case 3: Only a 4-digit year
            if val_str.isdigit() and len(val_str) == 4:
                cleaned_ds.append(datetime(int(val_str), 1, 1))
                continue

            # Case 4: Try parsing normally (handles things like '2023-06-15', '15/06/2023', etc.)
            parsed = pd.to_datetime(val_str, errors='coerce')
            cleaned_ds.append(parsed if not pd.isna(parsed) else None)

        except:
            cleaned_ds.append(None)

    df = pd.DataFrame({'ds': cleaned_ds, 'y': y_raw})
    df = df.dropna(subset=['ds', 'y'])

    # Ensure 'y' is numeric
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df = df.dropna(subset=['y'])

    # Optional: remove dates far in the past
    df = df[df['ds'] >= pd.Timestamp("2000-01-01")]

    df = df.sort_values('ds').reset_index(drop=True)
    return df

@app.route('/api', methods=['POST'])
def process():
    try:
        data = request.json

        system_name = data.get('system', 'Guest')
        interval = data.get('interval', 5)  # how many steps to forecast
        dataset = data.get('dataset', [])   # list of y values
        date_values = data.get('date_values', [])  # list of raw date values
        project_id = data.get('project_id', 777)

        if len(dataset) != len(date_values):
            return jsonify({"error": "Length of dataset and date_values must be equal"}), 400

        # ✅ Clean and prepare dataset for Prophet
        df = clean_and_prepare_for_prophet(date_values, dataset)

        if df.empty:
            return jsonify({"error": "No valid date/value pairs after cleaning"}), 400

        # ✅ Train Prophet model
        model = Prophet()
        model.fit(df)

        # ✅ Forecast future steps
        future = model.make_future_dataframe(periods=interval, freq='Y')  # yearly forecast
        forecast = model.predict(future)

        # Get only future forecasted values
        future_forecast = forecast[forecast['ds'] > df['ds'].max()]
        forecast_values = future_forecast[['ds', 'yhat']].to_dict(orient='records')

        # ✅ Simple accuracy estimate using naive method
        train_size = int(len(df) * 0.4)
        train, test = df['y'][:train_size], df['y'][train_size:]

        if len(test) > 0:
            last_train_value = train.iloc[-1]
            naive_forecast = [last_train_value] * len(test)
            mape = round(mean_absolute_percentage_error(test, naive_forecast) * 100, 2)
            accuracy = round(100 - mape, 2)
        else:
            mape = None
            accuracy = None

        # ✅ Save the model
        save_folder = "models"
        os.makedirs(save_folder, exist_ok=True)
        model_name = f"timeseries_{project_id}"
        file_path = os.path.join(save_folder, model_name + ".pkl")

        with open(os.devnull, 'w'), contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
            joblib.dump(model, file_path)

        return jsonify({
            "message": {
                "ds" : [1,2,3,4,5], 
                "forecasts": forecast_values,
                "accuracy": accuracy,
                "mape": mape,
                "model_type": "prophet_model",
                "model_name": model_name
            },
            "status": "saved",
             
        }), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
