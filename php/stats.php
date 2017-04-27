<html>

<head>
<link rel="stylesheet" type="text/css" href="../css/style2.css">
</head>

<body>

<?php

include 'lib/connectDb.php';

echo "<H1>statistics</H1>\n";


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
order by mo asc
limit 1000
;";


if($result = mysqli_query($link, $sql)){
	
	$rowcount=mysqli_num_rows($result);
	$sumHours=0;	
    if($rowcount > 0){
        $outDataSt="var theDataSt=[\n";

        $outTable="<table border=2>\n";
        $outTable.="<tr>";
                $outTable.="<th>month</th>";
				$outTable.="<th>observations QTY</th>";                
                $outTable.="<th>days QTY</th>";    
                $outTable.="<th>total exposure duration(hours)</th>";                
                $outTable.="<th>average observation duration(hours)</th>";                
            $outTable.="</tr>\n";
        while($row = mysqli_fetch_array($result)){
            
            $outDataSt.="{ 'date':'". $row['mo'] . "', 'hours':" . round($row['hours'],2) . "},";
            $sumHours+=$row['hours'];

            $outTable.="<tr>";
                $outTable.="<td>" . $row['mo'] . "</td>";
                $outTable.="<td>" . $row['obs'] . "</td>";
                $outTable.="<td>" . $row['night'] . "</td>";
                $outTable.="<td>" . round($row['hours'],0) . "</td>";
                $outTable.="<td>" . round($row['hours']/$row['obs'],1) . "</td>";

            $outTable.="</tr>\n";
        }
        
        $outDataSt=rtrim($outDataSt,","). "]\n";

        $outTable.="</table>";
        // Close result set
        mysqli_free_result($result);
    } else{
        $outTable="No records matching your query were found.";
    }
} else{
    $outTable="ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

// Close connection
mysqli_close($link);

echo "Total " . round($sumHours,1) ." Hours of exposure time. <p>";

?>

<script src="https://d3js.org/d3.v4.min.js"></script>


<style>

.bar {
  fill: steelblue;
}

.bar:hover {
  fill: brown;
}

.axis--x path {
  display: none;
}

</style>
<svg width="1800" height="500"></svg>

<script>

<?php
echo $outDataSt;
?>

var svg = d3.select("svg"),
    margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom;

var x = d3.scaleBand().rangeRound([0, width]).padding(0.1),
    y = d3.scaleLinear().rangeRound([height, 0]);

var g = svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  x.domain(theDataSt.map(function (d) { return d.date;}));
  y.domain([0, d3.max(theDataSt, function (d) { return d.hours;})]);

  g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y).ticks(10));

    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .attr("text-anchor", "end")
      .text("hours");

  g.selectAll(".bar")
      .data(theDataSt)
      .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.date);})
      .attr("y", function(d) { return y(d.hours);})
      .attr("width", x.bandwidth())
      .attr("height", function(d) { return height - y(d.hours);} );


</script>

<?php
echo $outTable;
?>

