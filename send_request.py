import requests

dataset = [1,2,3,4,5]

url = "http://127.0.0.1:5000/load_model"
data = {
    "system": "Innocent",
    "model-name": "auto_arima_model_53494",
    "interval": 5
}
response = requests.post(url, json=data)

print(response.json())
