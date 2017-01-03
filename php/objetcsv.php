<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

include 'lib/connectDb.php';


$conn=connectDb();

$result = $conn->query("SELECT objectid, alpha, delta,FLUX_V,(FLUX_B-FLUX_V) as Bmv FROM object");

$outp = "id,RAh,RAm,RAs,DEd,DEm,DEs,Vmag,BmV\n";
while($rs = $result->fetch_array(MYSQLI_ASSOC)) {
	list($Rah, $Ram, $Ras) = explode(" ", $rs["alpha"]."  ");
	list($Ded, $Dem, $Des) = explode(" ", $rs["delta"]."  ");

    $outp .= $rs["objectid"]. ',';
    $outp .= $Rah. ',' .$Ram. ','.  $Ras. ',';
    $outp .= $Ded. ',' . $Dem. ',' .$Des. ',';
    $outp .= $rs["FLUX_V"]     .",";
    $outp .= $rs["Bmv"]     ."\n"; 
}

$conn->close();

echo($outp);
?>
