<html>

<head>
<link rel="stylesheet" type="text/css" href="../css/style2.css">
</head>

<body>

<script src="https://d3js.org/d3.v4.min.js"></script>



<?php

include 'lib/connectDb.php';

echo "<H2>stats</H2>\n";

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

echo '<form action="stats.php" method="post">';
echo '<p>object name ';
echo '    <input type="text" name="searchStar" value="'.$searchStar .'"/>';
echo ' project ';
echo '    <input type="text" name="projectName" value="'.$projectName .'"/>';
echo ' status';
echo '    <input type="text" name="statusValue" value="'.$statusValue .'"/>';
echo '';
echo '    <input type="submit"  value="apply filter" />';
echo '</form>';



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
order by mo desc
limit 1000
;";


if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
		
    if($rowcount > 0){
        echo "<table border=2>\n";
            echo "<tr>";
                echo "<th>month</th>";
				echo "<th>observations QTY</th>";                
                echo "<th>days QTY</th>";    
                echo "<th>total exposure duration(hours)</th>";                
                echo "<th>average observation duration(hours)</th>";                
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['mo'] . "</td>";
                echo "<td>" . $row['obs'] . "</td>";
                echo "<td>" . $row['night'] . "</td>";
                echo "<td>" . round($row['hours'],0) . "</td>";
                echo "<td>" . round($row['hours']/$row['obs'],2) . "</td>";

            echo "</tr>\n";
        }
        echo "</table>";
        // Close result set
        mysqli_free_result($result);
    } else{
        echo "No records matching your query were found.";
    }
} else{
    echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


// Close connection
mysqli_close($link);

?>

