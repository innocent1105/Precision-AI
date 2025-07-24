import pmdarima
from pmdarima import auto_arima
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import json


data = [122, 188,173,157,197,157,197, 173,173,157,197,122, 188,122, 188, 173,122, 188,157,197]
df = pd.Series(data)

forecast_interval = 10 

model = auto_arima(df, seasonal=False, suppress_warnings=True)

# print(model.summary)


# forecast
forecast = model.predict(n_periods=forecast_interval)
forecasts = forecast.values
print(forecasts.tolist())



# plt.plot(df, label="Original data")
# plt.plot(range(len(df), len(df) + forecast_interval), forecast, label="forecasts")
# plt.legend()
# plt.show()





















# accuracy and performance test
# split the data in equal len() parts
# Split the data (80% train, 20% test)
train_size = int(len(data) * 0.8)
train, test = data[:train_size], data[train_size:]

# Train a simple forecasting model (here we use the last value of train as prediction)
last_train_value = train[-1]
forecast = [last_train_value] * len(test)  # Naive forecast (last train value repeated)

# Calculate MAPE
mape = mean_absolute_percentage_error(test, forecast) * 100

# Calculate accuracy
accuracy = 100 - mape

# Display results
print(f"MAPE: {mape:.2f}%")
print(f"Accuracy: {accuracy:.2f}%")


model_data = [forecasts, accuracy, mape]
# model_data = json.dumps(model_data)

print(model_data)


