

<link rel="stylesheet" type="text/css" href="../css/style2.css">

<?php

include 'lib/connectDb.php';

echo "<H2>Observations</H2>";

$link=connectDb();

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


echo '<form action="obsTable.php" method="post">';
echo '<p>object name ';
echo '    <input type="text" name="searchStar" value="'.$searchStar .'"/>';
echo ' project ';
echo '    <input type="text" name="projectName" value="'.$projectName .'"/>';
echo ' status';
echo '    <input type="text" name="statusValue" value="'.$statusValue .'"/>';
echo '';
echo '    <input type="submit"  value="apply filter" />';
echo '</form>';


error_reporting(E_ALL);
if(!empty($_POST['choix']))
{
	echo 'Les observations cochées sont : ';
	foreach($_POST['choix'] as $val)
	{
		echo $val,',';
	}

}


// Attempt select query execution
$sql = "select observation.obsId,observation.dateObs,
observer.alias as observer,
site.name as siteName,
object.objectId as objId,
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
where object.name like '". $searchStar. "%'  and project.name like '".$projectName. "%' and observation.status like '".$statusValue."%'
order by observation.dateObs DESC ";

//echo $sql;

if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
	
	echo $rowcount." observations entry.<br>";
		
    if($rowcount > 0){
//		echo "nb result=" . $result . "<br>";


		echo '<br /> <form method="POST" action="execPython.php">';
		echo '<input type="submit" value="EnvoyerFichiersRaw vers pipeline de traitement">';
		echo '<input type="hidden" name="pythonScriptName" value="extractRaw" />';
		
        echo "\n<table>";
            echo "<tr>";
                echo "<th></th>";
  				echo "<th>obsId</th>";
                echo "<th>dateObs (UTC)</th>";
                echo "<th>site</th>";
                echo "<th>project</th>";
                echo "<th>REF</th>";
                echo "<th>objId</th>";
                echo "<th>object name</th>";
                echo "<th>bayer name</th>";
                echo "<th>object description</th>";
                echo "<th>SpType</th>";            
                echo "<th>MagV</th>";            
                echo "<th>instrument</th>";
                echo "<th>status</th>";
            echo "</tr>\n";
        while($row = mysqli_fetch_array($result)){
            echo "<tr>";
                echo '<td><input type="checkbox" name="choix[]" value="'.$row['obsId'].'"><br></td>';
                echo '<td><a href="filenameTable.php?obsId='.$row['obsId'].'">'. $row['obsId'] . '</a></td>';				
                echo "<td>" . $row['dateObs'] . "</td>";
                echo "<td>" . $row['siteName'] . "</td>";
                echo "<td>" . $row['projName'] . "</td>";
                echo "<td>" . $row['isRef'] . "</td>";
                echo "<td>" . $row['objId'] . "</td>";
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
