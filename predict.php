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
include("./connection.php");
header("Content-Type: application/json");

// === Read and decode raw input ===
$rawInput = file_get_contents("php://input");
$data = json_decode($rawInput, true);

$model_id = $data['model_id'];
$user_id = $data['user_id'];

$sql = "SELECT * FROM models WHERE user_id = '$user_id' AND model_id = '$model_id' LIMIT 1";
$result = mysqli_query($con, $sql);

if ($result && $result->num_rows > 0) {
    $row = $result->fetch_assoc();
    $model_name = $row['model_name'];

    $payload = [
        "system" => "Precision-ai",
        "model_name" => $model_name
    ];

    $ch = curl_init("http://127.0.0.1:5001/predict");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlError = curl_error($ch);
    curl_close($ch);

    $responseData = json_decode($response, true);

    

    http_response_code($httpCode);
    echo json_encode($responseData);
    
    exit();
} else {
    http_response_code(404);
    echo json_encode(["error" => "Model not found"]);
    exit();
}
