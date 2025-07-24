<?php
// URL of your Flask API endpoint
$url = "http://127.0.0.1:5000/process";


$dataset = [10,20,30,40,50,60,70,80,90,103,141];

$project_name = "Project_1";
$user_id = "23721";
$project_id = 0;

function generate_project_id(){
    $project_id = $GLOBALS['project_id'];
    for ($i=0; $i < 10; $i++) { 
        $random_number = random_int(1577, 7777);
        $project_id = $project_id + $random_number;
    }
    return $project_id;
}

$project_id = generate_project_id();
echo $project_id;

// Data to send in the POST request
$data = array(
    "system" => "precision",
    "interval" => 20,
    'dataset' => $dataset,
    'project_id' => $project_id
);

// Encode data to JSON format
$jsonData = json_encode($data);

// Initialize cURL
$ch = curl_init($url);

// Set cURL options
curl_setopt($ch, CURLOPT_POST, true);                         // Specify POST request
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));  // Set JSON content type
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);              // Attach JSON data
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);               // Return the response

// Execute cURL request
$response = curl_exec($ch);

// Check for errors
if ($response === false) {
    echo "cURL Error: " . curl_error($ch);
} else {
    // Decode and display the response
    echo "Response from API: " . $response;
}

// Close cURL session
curl_close($ch);
?>
