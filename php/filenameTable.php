
<head>
<link rel="stylesheet" type="text/css" href="../css/style2.css">
</head>

<?php

include 'lib/connectDb.php';


$link=connectDb();


error_reporting(E_ALL);
if(empty($_GET['obsId']))
{
	echo "<H1>All files in archive..</H1>";
    echo "Do not display, this table is to long..<br>";
    echo "use  filenameTable?obsId=...<br>";
    exit;
}
else
{

    echo "<H1>Observation Id=".$_GET['obsId']."</H2>";

	echo "<H2>Raw files</H2>";

}

// Attempt select query execution
$sql = "select * from fileName where obsId=".$_GET['obsId']." AND phase='RAW'ORDER by date,filetype,filename";

//echo $sql;

if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
	
		
    if($rowcount > 0){
		
		
        echo "\n<table border=2>";
            echo "<tr>";
  				echo "<th>fileId</th>";
                echo "<th>phase</th>";
                echo "<th>filetype</th>";
                echo "<th>filename</th>";
                echo "<th>dateObs(UTC)</th>";
                echo "<th>serieId</th>";         
                echo "<th>tempCCD(°C)</th>";
                echo "<th>binning</th>";
                echo "<th>detector</th>";            
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['fileId'] . "</td>";				
                echo "<td>" . $row['phase'] . "</td>";
                echo "<td>" . $row['filetype'] . "</td>";
                echo "<td>" . $row['filename'] . "</td>";
                echo "<td>" . $row['date'] . "</td>";
                echo "<td>" . $row['serieId'] . "</td>";
                echo "<td>" . $row['tempCCD'] . "</td>";
                echo "<td>" . $row['binning'] . "</td>";
                echo "<td>" . $row['detector'] . "</td>";
            echo "</tr>\n";
        }
        echo "</table>";
        echo '</form>';
        echo $rowcount." files.<br>";

        // Close result set
        mysqli_free_result($result);
    } else{
        echo "No records matching your query were found.";
    }
} else{
    echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

echo "<H2>Other files </H2>";

// Attempt select query execution
$sql = "select * from fileName where obsId=".$_GET['obsId']." AND NOT phase='RAW'  ORDER by date,filetype,filename";

//echo $sql;

if($result = mysqli_query($link, $sql)){
    
    $rowcount=mysqli_num_rows($result);
        
    if($rowcount > 0){
        
        
        echo "\n<table border=2>";
            echo "<tr>";
                echo "<th>fileId</th>";
                echo "<th>phase</th>";
                echo "<th>filetype</th>";
                echo "<th>filename</th>";
                echo "<th>date</th>";
                      
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['fileId'] . "</td>";             
                echo "<td>" . $row['phase'] . "</td>";
                echo "<td>" . $row['filetype'] . "</td>";
                echo "<td>" . $row['filename'] . "</td>";
                echo "<td>" . $row['date'] . "</td>";
            echo "</tr>\n";
        }
        echo "</table>";
        echo '</form>';
        echo $rowcount." files.<br>";

        // Close result set
        mysqli_free_result($result);
    } else{
        echo "No records matching your query were found.";
    }
} else{
    echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

echo "<h2>Reduced spectrums</h2>";
$sql = "select * from fileSpectrum where obsId=".$_GET['obsId']." ORDER by dateObs,orderNo";
//echo $sql;
if($result = mysqli_query($link, $sql)){
    
    $rowcount=mysqli_num_rows($result);
    
        
    if($rowcount > 0){
        
        
        echo "\n<table border=2>";
            echo "<tr>";
                echo "<th>fileId</th>";
                echo "<th>filename</th>";
                echo "<th>dateObs(UTC)</th>";
                echo "<th>exposure(s)</th>";
                echo "<th>start(A)</th>";
                echo "<th>stop(A)</th>";
                echo "<th>orderNo</th>";            
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['fileId'] . "</td>";             
                echo "<td>" . $row['filename'] . "</td>";
                echo "<td>" . $row['dateObs'] . "</td>";
                echo "<td>" . $row['expTime'] . "</td>";
                echo "<td>" . $row['lStart'] . "</td>";
                echo "<td>" . $row['lStop'] . "</td>";
                echo "<td>" . $row['orderNo'] . "</td>";
            echo "</tr>\n";
        }
        echo "</table>";
        echo '</form>';
        echo $rowcount." files.<br>";

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
