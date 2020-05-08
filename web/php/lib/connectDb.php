<?php

function connectDb() {

	$string = file_get_contents("../python/config/config.json");
	$json_a = json_decode($string, true);
	$host=$json_a['db']['host'];
	$user=$json_a['db']['userName'];
	$pass=$json_a['db']['password'];
	$dataBase=$json_a['db']['dataBase'];

	$conn = new mysqli($host, $user, $pass, $dataBase);

	return $conn;

}

?>