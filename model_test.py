import joblib
from prophet import Prophet

# Load the model using joblib
model = joblib.load("models/timeseries_6278.pkl")

# Make future dataframe and predict
future = model.make_future_dataframe(periods=5)
forecast = model.predict(future)

# Print the last 5 forecasted values
print(forecast[['ds', 'yhat']].tail(5))
