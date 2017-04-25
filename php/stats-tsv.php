<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

include 'lib/connectDb.php';

if(!empty($_POST['searchStar']))
{ $searchStar=$_POST['searchStar'];	}
else 
{ $searchStar=""; }

if(!empty($_POST['projectName']))
{ $projectName=$_POST['projectName']; }
else 
{ $projectName=""; }

if(!empty($_POST['statusValue']))
{ $statusValue=$_POST['statusValue']; }
else 
{ $statusValue=""; }

$link=connectDb();

// Attempt select query execution
//$sql = "select * from object order by alpha";

$sql = "select substring(dateObs,1,7)  as mo, count(DISTINCT observation.obsId) as obs,
count(DISTINCT substring(observation.dateObs,1,11)) as night, 
 sum(expTime)/3600 as hours
from observation
left join fileName on fileName.obsId=observation.obsId
left join object on object.objectId=observation.objId
left join project on project.projectId =observation.projectId
where (object.name like '". $searchStar. "%' or object.bayerName like '". $searchStar. "%' ) 
AND fileName.phase='RAW' and project.name like '".$projectName. "%'
AND observation.status like '".$statusValue."%'
group by mo
order by mo asc
limit 1000
;";


$outp = "date\tfrequency\t\n";

$result = mysqli_query($link, $sql);

while($rs = $result->fetch_array(MYSQLI_ASSOC)) {
	$outp .= $rs["mo"]. "\t";
    $outp .= $rs["hours"]     ."\n"; 
}

mysqli_close($link);
echo($outp);
?>

