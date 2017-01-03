#!/bin/bash

function getJsonVal () { 
    python -c "import json,sys;sys.stdout.write(json.dumps(json.load(sys.stdin)$1))"; 
}

cat ../config/config.json 
echo

_pass=`cat ../config/config.json | getJsonVal "['db']['password']" | tr -d '"' `
_user=`cat ../config/config.json | getJsonVal "['db']['userName']" | tr -d '"' `
_dataBase=`cat ../config/config.json | getJsonVal "['db']['dataBase']" | tr -d '"' `
_base=`cat ../config/config.json | getJsonVal "['path']['archive']" | tr -d '"' `


echo Repertoire base de donne $_base

now=$(date +%Y_%m_%d_%H_%M_%S)
_sql_dumps="$_base/DumpSQL"
_sql_file="$_sql_dumps/$now.sql"

#mysqldump --user robot --password=xxxxx spectro > $_sql_file
echo DumpSQL vers $_sql_file
mysqldump --user $_user   --password=$_pass $_dataBase > $_sql_file
drive push -no-prompt -verbose $_sql_dumps
drive push -no-prompt -verbose $_base/archive/2016/12
