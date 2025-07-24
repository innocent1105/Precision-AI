<?php

include("./connection.php");

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

// Receive raw POST JSON
$payload = json_decode(file_get_contents("php://input"), true);

// Check if 'data' exists
if (!isset($payload['data'])) {
    echo json_encode("invalid-request");
    exit();
}

$data = $payload['data'];

$email = $data['email'] ?? '';
$password = $data['password'] ?? '';

// Validate inputs
if (empty($email)) {
    echo json_encode("error-1"); // Missing email
    exit();
}

if (empty($password)) {
    echo json_encode("error-3"); // Missing password
    exit();
}

// Sanitize email input
$email = mysqli_real_escape_string($con, $email);

// Check user
$qry = "SELECT * FROM users WHERE email = '$email' LIMIT 1";
$result = mysqli_query($con, $qry);

if ($result && mysqli_num_rows($result) > 0) {
    $row = mysqli_fetch_assoc($result);

    if (password_verify($password, $row['password'])) {
        $user_data = [
            "user_id" => $row['user_id'],
            "email" => $row['email'],
            "username" => $row['username'],
            "status" => "success"
        ];
        echo json_encode($user_data);
        exit();
    } else {
        echo json_encode("wrong-password");
        exit();
    }
} else {
    echo json_encode("error-1"); // User not found
    exit();
}
?>
