

<link rel="stylesheet" type="text/css" href="../css/style2.css">

<?php

include 'lib/connectDb.php';

echo "<H2>Detector calibration: bias & offset </H2>";

$link=connectDb();

if(!empty($_POST['searchCCD']))
{ $searchCCD=$_POST['searchCCD'];	}
else 
{ $searchCCD=""; }

if(!empty($_POST['searchImageType']))
{ $searchImageType=$_POST['searchImageType']; }
else 
{ $searchImageType=""; }

echo '<form action="calibDetector.php" method="post">';
echo '<p>CCD name ';
echo '    <input type="text" name="searchCCD" value="'.$searchCCD .'"/>';
echo ' image type (BIAS,DARK) ';
echo '    <input type="text" name="searchImageType" value="'.$searchImageType .'"/>';
echo '';
echo '    <input type="submit"  value="apply filter" />';
echo '</form>';


error_reporting(E_ALL);
if(!empty($_POST['choix']))
{
	echo 'Les champs du POST sont sont : ';
	foreach($_POST['choix'] as $val)
	{
		echo $val,',';
	}

}



// select request
$sql= "select 
fileName.serieId as serieId,
MAX(fileName.destDir) as path,
MAX(fileName.detector) as detector, 
MAX(fileName.filetype) as fileType,
MAX(fileName.binning) as binning,
format(AVG(fileName.tempCCD),'N1') as temperature,
AVG(fileName.expTime) as expTime, 
count(*) as nbExposure

FROM fileName

WHERE 
detector like '". $searchCCD. "%' 
and filetype in ('DARK','BIAS')
and filetype like '".$searchImageType."%'

group by fileName.serieId
order by serieId DESC";

//echo $sql;

if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
	
	echo $rowcount." Detector calibration entry.<br>";
		
    if($rowcount > 0){
//		echo "nb result=" . $result . "<br>";


		echo '<br />';		
        echo "<table>";
            echo "<tr>";
                echo "<th>serieId</th>";
                echo "<th>path</th>";
                echo "<th>detector</th>";
                echo "<th>fileType</th>";
                echo "<th>binning</th>";
                echo "<th>temperature(°C)</th>";
                echo "<th>expTime(s)</th>";
                echo "<th>nbExposure</th>";
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['serieId'] . "</td>";
                echo "<td>" . $row['path'] . "</td>";
                echo "<td>" . $row['detector'] . "</td>";
                echo "<td>" . $row['fileType'] . "</td>";
                echo "<td>" . $row['binning'] . "</td>";
                echo "<td>" . $row['temperature'] . "</td>";
                echo "<td>" . $row['expTime'] . "</td>";
                echo "<td>" . $row['nbExposure'] . "</td>";
            echo "</tr>\n";
        }
        echo "</table>\n";
        echo '</form>';
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
