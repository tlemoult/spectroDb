<html>

<head>
<link rel="stylesheet" type="text/css" href="../css/style2.css">
</head>

<body>

<script src="https://d3js.org/d3.v4.min.js"></script>



<?php

include 'lib/connectDb.php';

echo "<H2>Objects table</H2>\n";

$link=connectDb();


// Attempt select query execution
//$sql = "select * from object order by alpha";

$sql = "select DISTINCT object.name as name,bayerName,noHD,OTYPE_V,alpha,delta,FLUX_V,FLUX_B,FLUX_R,FLUX_K,FLUX_H,RV_VALUE,SP_TYPE,MK_Spectral_type,project.name as projectName from object
LEFT join observation on object.objectId=observation.objId
LEFT join project on observation.projectId=project.projectId
ORDER BY project.name,SP_TYPE;";


if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
	
	echo $rowcount." objects entry.<br>\n";
		
    if($rowcount > 0){
        echo "<table border=2>\n";
            echo "<tr>";
				echo "<th>Project</th>";
                echo "<th>name</th>";
                echo "<th>bayerName</th>";
                echo "<th>noHD</th>";
                echo "<th>OTYPE_V</th>";         
                echo "<th>alpha</th>";
                echo "<th>delta</th>";
                echo "<th>FLUX_V</th>";
                echo "<th>FLUX_B</th>";            
                echo "<th>FLUX_R</th>";            
                echo "<th>FLUX_K</th>";
                echo "<th>FLUX_H</th>";
                echo "<th>RV_VALUE</th>";
                echo "<th>SP_TYPE</th>";
                echo "<th>MK_Spectral_type</th>";
                
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
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

