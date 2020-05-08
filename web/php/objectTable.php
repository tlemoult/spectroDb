<html>

<head>
<link rel="stylesheet" type="text/css" href="../css/style2.css">
</head>

<body>

<script src="https://d3js.org/d3.v4.min.js"></script>



<?php

include 'lib/connectDb.php';

echo "<H2>Objects table</H2>\n";
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

echo '<form action="objectTable.php" method="post">';
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

$sql = "select DISTINCT object.objectId as objId,
object.name as name,bayerName,noHD,OTYPE_V,alpha,delta,FLUX_V,FLUX_B,FLUX_R,FLUX_K,FLUX_H,RV_VALUE,SP_TYPE,MK_Spectral_type,project.name as projectName 
from object
LEFT join observation on object.objectId=observation.objId
LEFT join project on observation.projectId=project.projectId
where (object.name like '". $searchStar. "%' or object.bayerName like '". $searchStar. "%' ) 
AND project.name like '".$projectName. "%'
AND observation.status like '".$statusValue."%'
ORDER BY project.name,SP_TYPE;";


if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
	
	echo $rowcount." objects entry.<br>\n";
		
    if($rowcount > 0){
        echo "<table border=2>\n";
            echo "<tr>";
                echo "<th>ObjId</th>";
				echo "<th>Project</th>";
                echo "<th>name</th>";
                echo "<th>bayerName</th>";
                echo "<th>noHD</th>";
                echo "<th>OTYPE_V</th>";         
                echo "<th>alpha</th>";
                echo "<th>delta</th>";
                echo "<th>MagV</th>";
                echo "<th>MagB</th>";            
                echo "<th>MagR</th>";            
                echo "<th>MagK</th>";
                echo "<th>MagH</th>";
                echo "<th>RV_VALUE</th>";
                echo "<th>SP_TYPE</th>";
                echo "<th>MK_Spectral_type</th>";
                
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['objId'] . "</td>";
                echo "<td>" . $row['projectName'] . "</td>";
                echo "<td>" . $row['name'] . "</td>";
                echo "<td>" . $row['bayerName'] . "</td>";
                echo "<td>" . $row['noHD'] . "</td>";
                echo "<td>" . $row['OTYPE_V'] . "</td>";
                echo "<td>" . $row['alpha'] . "</td>";
                echo "<td>" . $row['delta'] . "</td>";
                echo "<td>" . $row['FLUX_V'] . "</td>";
                echo "<td>" . $row['FLUX_B'] . "</td>";
                echo "<td>" . $row['FLUX_R'] . "</td>";
                echo "<td>" . $row['FLUX_K'] . "</td>";
                echo "<td>" . $row['FLUX_H']. "</td>";
                echo "<td>" . $row['RV_VALUE']. "</td>";
                echo "<td>" . $row['SP_TYPE']. "</td>";
                echo "<td>" . $row['MK_Spectral_type']. "</td>";
                
                
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

