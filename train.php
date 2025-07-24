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

$user_data = $data['user_data']['data'];
$user_id = $user_data['user_id'];
$email = $user_data['email'];
$status = $user_data['status'];

function cleanAndPrepareForProphet($ds_raw, $y_raw){
    $cleaned_ds = [];
    $cleaned_y = [];

    for ($i = 0; $i < count($ds_raw); $i++) {
        $val = $ds_raw[$i];
        $parsed = null;

        // Try to parse date directly
        if (strtotime($val)) {
            $parsed = date('Y-m-d', strtotime($val));
        }
        // Check if it's just a year like "2022"
        elseif (ctype_digit($val) && strlen($val) == 4) {
            $parsed = $val . '-01-01';
        }else{
            $parsed = 2025 . '-01-01'; 
        }

        // Add only if ds and y are valid
        $y_val = $y_raw[$i];
        if ($parsed !== null && is_numeric($y_val)) {
            $cleaned_ds[] = $parsed;
            $cleaned_y[] = (float) $y_val;
        }else{
            $cleaned_ds[] = $parsed;
            preg_match('/\d+(\.\d+)?/', $y_val, $y_val);
            $cleaned_y[] = (float) $y_val; 
        }
    }

    // Combine into structured array (like a DataFrame)
    $data = [];
    for ($i = 0; $i < count($cleaned_ds); $i++) {
        $data[] = [
            'ds' => $cleaned_ds[$i],
            'y' => $cleaned_y[$i]
        ];
    }

    // Sort by 'ds' date
    usort($data, function($a, $b) {
        return strtotime($a['ds']) - strtotime($b['ds']);
    });

    return $data;
}

if($status == "success"){
        
    // === Extract key fields ===
    $targetColumnId = $data['target']['id'];
    $targetColumn = $data['targetColumn']['data'];
    $datetimeId = $data['datetime']['id'];
    $datetime = $data['import_data']['data']['data'][$datetimeId];



    // === Remove headers like "Values" or "Timeline"
    array_shift($targetColumn);
    array_shift($datetime);


    // === Decode projectData ===
    $projectDataJson = $data['project_data']['data'];
    $projectData = json_decode($projectDataJson, true);

    $projectDetails = $projectData['projectDetails'] ?? [];
    $forecastSettings = $projectData['forecastSettings']['settings'] ?? [];

    $projectId = rand(1000, 7000);
    $ProjectName = $projectDetails['projectName'];
    $interval = 5;


    $cleanDataset = [];
    $cleanDatetime = [];

    for ($i = 0; $i < count($targetColumn); $i++) {
        if (!is_null($targetColumn[$i]) && isset($datetime[$i])) {
            $cleanDataset[] = $targetColumn[$i];
            $cleanDatetime[] = $datetime[$i];
        }
    }

    file_put_contents('debug.log', json_encode([
        'datetime_raw' => $cleanDatetime,
        'values_raw' => $cleanDataset
    ], JSON_PRETTY_PRINT));
    

    $clean_dataset = cleanAndPrepareForProphet($cleanDatetime, $cleanDataset);


    $payload = [
        "system" => "Precision-ai",
        "dataset" => $cleanDataset,
        "date_values" => $cleanDatetime,
        "project_id" => $projectId
    ];


    $ch = curl_init("http://localhost:7000/api");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    http_response_code($httpCode);

    $responseData = json_decode($response, true);

    if (!$responseData) {
        echo json_encode(["error" => "Invalid JSON response from Python"]);
        exit();
    }


    $accuracy     = $responseData['message']['accuracy'];
    $mape         = $responseData['message']['mape'];
    $modelName    = $responseData['message']['model_name'];
    $modelType    = $responseData['message']['model_type'];
    $forecastData = $responseData['message']['forecasts'];

    $model_id = (rand(20000, 700000) / 4) * rand(100, 500);

    $sql = "insert into models (user_id, model_id, model_name, model_type) values ('$user_id', '$model_id', '$modelName', '$modelType')";
    $result = mysqli_query($con, $sql);

    if($result){
        echo json_encode([
            "accuracy" => $accuracy,
            "mape" => $mape,
            "model_name" => $modelName,
            "model_id" => $model_id,
            "model_type" => $modelType,
            "forecasts" => $forecastData,
            "dataset" => $clean_dataset,
            "status" => "success"
        ]);
        exit; 
    }else{
        echo json_encode([
            "status" => "error - failed to save model"
        ]);
        exit; 
    }

}else{
    echo json_encode("unknown user");
    exit;
}







