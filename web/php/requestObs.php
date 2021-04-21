
<head>
<link rel="stylesheet" type="text/css" href="../css/style2.css">
</head>

<?php

include 'lib/connectDb.php';

echo "<H2>Observation requests.</H2>";

$link=connectDb();

// Attempt select query execution
$sql = "SELECT RequestToObserveList.uid,RequestToObserveList.priority,project.name as project,object.name as object,object.FLUX_V,
object.alpha as alpha, object.delta as delta,
RequestToObserveList.ExposureTime,RequestToObserveList.NbExposure,RequestToObserveList.TotExposure,
RequestToObserveList.intTime,RequestToObserveList.period,RequestToObserveList.lastObs,
RequestToObserveList.config,RequestToObserveList.calib
FROM RequestToObserveList 
LEFT JOIN object ON RequestToObserveList.objectId=object.objectId 
LEFT JOIN project ON RequestToObserveList.projectId=project.projectId
order by alpha,delta
";


if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
		
	echo $rowcount." request for observation.<br>";
		
    if($rowcount > 0){
//		echo "nb result=" . $result . "<br>";
        echo "<table border=2>";
            echo "<tr>";
                echo "<th>uid</th>";            
                echo "<th>Priority</th>";
                echo "<th>Project</th>";
                echo "<th>object</th>";
                echo "<th>alpha</th>";
                echo "<th>delta</th>";
                echo "<th>Mag V</th>";         
                echo "<th>ExposureTime</th>";
                echo "<th>NbExposure</th>";
                echo "<th>TotExposure</th>";
                echo "<th>intTime</th>";            
                echo "<th>periode</th>";            
                echo "<th>lastObs</th>";
                echo "<th>config</th>";
                echo "<th>calib</th>";
                
            echo "</tr>";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['uid'] . "</td>";
                echo "<td>" . $row['priority'] . "</td>";
                echo "<td>" . $row['project'] . "</td>";
                echo "<td>" . $row['object']. "</td>";
                echo "<td>" . $row['alpha']. "</td>";
                echo "<td>" . $row['delta']. "</td>";
                echo "<td>" . $row['FLUX_V'] . "</td>";
                echo "<td>" . $row['ExposureTime'] . "</td>";
                echo "<td>" . $row['NbExposure'] . "</td>";
                echo "<td>" . $row['TotExposure'] . "</td>";
                echo "<td>" . $row['intTime'] . "</td>";
                echo "<td>" . $row['period'] . "</td>";
                echo "<td>" . $row['lastObs'] . "</td>";
                echo "<td>" . $row['config'] . "</td>";
                echo "<td>" . $row['calib'] . "</td>";
                
                
            echo "</tr>";
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
