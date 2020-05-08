
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

///////////////////////////////////////////////////////////////
echo "<H1>Observation page</H2>";
$sql = "select observation.obsId,observation.dateObs,
observer.alias as observer,
site.name as siteName,
object.name as obj,
object.bayerName as obj2,
object.OTYPE_V as objtype,
object.SP_TYPE as objsptype,
object.FLUX_V as magV,
instrum.name as instr,observation.status,
project.name as projName,
observation.ref as isRef
from observation
left join object on object.objectId=observation.objId
left join instrum on instrum.instruId=observation.instruId
left join site on site.siteId=observation.siteId
left join observer on observer.observerID=observation.observerId
left join project on project.projectId =observation.projectId
where observation.obsId=".$_GET['obsId'];

if($result = mysqli_query($link, $sql)){
    
    $rowcount=mysqli_num_rows($result);
        
    if($rowcount > 0){
//      echo "nb result=" . $result . "<br>";
      
        echo "<table>";
            echo "<tr>";
                echo "<th>obsId</th>";
                echo "<th>dateObs (UTC)</th>";
                echo "<th>site</th>";
                echo "<th>project</th>";
                echo "<th>REF</th>";         
                echo "<th>target name</th>";
                echo "<th>bayer name</th>";
                echo "<th>target description</th>";
                echo "<th>SpType</th>";            
                echo "<th>MagV</th>";            
                echo "<th>instrument</th>";
                echo "<th>status</th>";
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['obsId'] . "</td>";
                echo "<td>" . $row['dateObs'] . "</td>";
                echo "<td>" . $row['siteName'] . "</td>";
                echo "<td>" . $row['projName'] . "</td>";
                echo "<td>" . $row['isRef'] . "</td>";
                echo "<td>" . $row['obj'] . "</td>";
                echo "<td>" . $row['obj2'] . "</td>";
                echo "<td>" . $row['objtype'] . "</td>";
                echo "<td>" . $row['objsptype'] . "</td>";
                echo "<td>" . $row['magV'] . "</td>";
                echo "<td>" . $row['instr'] . "</td>";
                echo "<td>" . $row['status']. "</td>";                
            echo "</tr>\n";
        }
        echo "</table>\n";
        // Close result set
        mysqli_free_result($result);
    } else{
        echo "No records matching your query were found.";
    }
} else{
    echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


echo "<H2>Acquisition raw files</H2>";


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
                echo "<th>path</th>";
                echo "<th>filename</th>";
                echo "<th>dateObs(UTC)</th>";
                echo "<th>serieId</th>";         
                echo "<th>exposure(s)</th>";
                echo "<th>tempCCD(°C)</th>";
                echo "<th>binning</th>";
                echo "<th>detector</th>";            
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['fileId'] . "</td>";				
                echo "<td>" . $row['phase'] . "</td>";
                echo "<td>" . $row['filetype'] . "</td>";
                echo "<td>" . $row['destDir'] . "</td>";                
                echo "<td>" . $row['filename'] . "</td>";
                echo "<td>" . $row['date'] . "</td>";
                echo "<td>" . $row['serieId'] . "</td>";
                echo "<td>" . $row['expTime'] . "</td>";
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

echo "<H2>Processing files</H2>";

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
                echo "<th>path</th>";
                echo "<th>filename</th>";
                echo "<th>date</th>";
                echo "<th>exposure(s)</th>";
                      
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo "<td>" . $row['fileId'] . "</td>";             
                echo "<td>" . $row['phase'] . "</td>";
                echo "<td>" . $row['filetype'] . "</td>";
                echo "<td>" . $row['destDir'] . "</td>";
                echo "<td>" . $row['filename'] . "</td>";
                echo "<td>" . $row['date'] . "</td>";
                echo "<td>" . $row['expTime'] . "</td>";
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

echo "<h2>Spectrums files</h2>";
$sql = "select * from fileSpectrum where obsId=".$_GET['obsId']." ORDER by dateObs,orderNo";
//echo $sql;
if($result = mysqli_query($link, $sql)){
    
    $rowcount=mysqli_num_rows($result);
    
        
    if($rowcount > 0){
        
        
        echo "\n<table border=2>";
            echo "<tr>";
                echo "<th>fileId</th>";
                echo "<th>path</th>";                
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
                echo "<td>" . $row['path'] . "</td>";
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
