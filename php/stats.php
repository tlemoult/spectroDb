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
?>

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

var svg = d3.select("svg"),
    margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = +svg.attr("width") - margin.left - margin.right,
    height = +svg.attr("height") - margin.top - margin.bottom;

var x = d3.scaleBand().rangeRound([0, width]).padding(0.1),
    y = d3.scaleLinear().rangeRound([height, 0]);

var g = svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.tsv("stats-tsv.php", function(d) {
  d.frequency = +d.frequency;
  return d;
}, function(error, data) {
  if (error) throw error;

  x.domain(data.map(function(d) { return d.date; }));
  y.domain([0, d3.max(data, function(d) { return d.frequency; })]);

  g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y).ticks(10, ""))
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .attr("text-anchor", "end")
      .text("Frequency");

  g.selectAll(".bar")
    .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.date); })
      .attr("y", function(d) { return y(d.frequency); })
      .attr("width", x.bandwidth())
      .attr("height", function(d) { return height - y(d.frequency); });
});

</script>



<?php
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

