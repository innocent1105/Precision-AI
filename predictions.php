<?php

// === CORS HEADERS ===
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization");

// === Handle preflight requests ===
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// === Setup ===
include("connection.php");
header("Content-Type: application/json");

// === Read and decode raw input ===
$rawInput = file_get_contents("php://input");
$data = json_decode($rawInput, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(["error" => "Invalid or missing JSON"]);
    exit();
}

// You can validate or extract fields as needed, e.g.:
$model_name = isset($data['model_name']) ? $data['model_name'] : null;
$user_id = isset($data['user_id']) ? $data['user_id'] : null;
$interval = isset($data['interval']) ? $data['interval'] : null;

if (!$model_name || !$user_id) {
    http_response_code(400);
    echo json_encode(["error" => "Missing model_name or user_id"]);
    exit();
}

// Prepare payload to send to Python server
$payload = json_encode([
    'interval' => $interval,
    'model_name' => $model_name,
    'user_id' => $user_id
]);

// Initialize cURL session to call Python Flask server
$ch = curl_init("http://127.0.0.1:7070/predict");  // Make sure this matches your Flask endpoint

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($payload)
]);

$response = curl_exec($ch);

if(curl_errno($ch)) {
    $error_msg = curl_error($ch);
    curl_close($ch);
    http_response_code(500);
    echo json_encode(["error" => "cURL error: $error_msg"]);
    exit();
}

$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

http_response_code($httpCode);

$responseData = json_decode($response, true);

// If the Python server response is not valid JSON, return error
// if ($responseData === null) {
//     echo json_encode(["error" => "Invalid JSON response from Python server"]);
//     exit();
// }

// Send back Python server response to client
echo json_encode($responseData);
exit();
