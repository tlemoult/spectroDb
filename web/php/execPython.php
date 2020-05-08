<?php 


$ObsId="";

echo "<h1>Execution script python</h1>";

if (!empty($_POST['pythonScriptName']))
{
  echo "pythonScriptName=".$_POST['pythonScriptName'];
  echo "<br>";
}
else
{
  echo "pythonScriptName non definis<br>";
}

if(!empty($_POST['choix']))
{
	foreach($_POST['choix'] as $val)
	{
		$ObsId.=" ".$val;
	}

}

 echo 'Les observations Id sont : ';
 echo $ObsId;


$pathScript='/home/tlemoult/Dropbox/python/spectroAutoPubli';

if ($_POST['pythonScriptName']=='extractRaw') 
{
	$script='/tools/get-raw-obs.py';
	
	$command = escapeshellcmd('python '.$pathScript.$script.' /mnt/audela-pipe/raw'.$ObsId);
	echo "<br>command=".$command."<br>";

#	$command = escapeshellcmd('/home/tlemoult/Dropbox/python/spectroAutoPubli/test/main.py '.$ObsId);
	$output = shell_exec($command);
	echo "<br><hr>Sortie du script python<br>";
	echo $output;
}
else
{
	echo "pythonScriptName incorrect<br>";
}
?>
