#!/bin/bash
echo $SHELL
echo $0

function getJsonVal () { 
    python -c "import json,sys;sys.stdout.write(json.dumps(json.load(sys.stdin)$1))"; 
}

_base=`cat ../config/config.json | getJsonVal "['path']['archive']" | tr -d '"' `


_now=$(date +%Y_%m_%d_%H_%M_%S)
_log_file="$_base/log/in.$_now.log"
_err_file="$_base/log/in.$_now.err"
_source_dir="$_base/in/"

echo "robot integration fichiers acquisitions" 
echo "source dir: $_source_dir"
echo "save log in $_log_file"
echo "save err in $_err_file"

python ../tools/in-raw.py $_source_dir > $_log_file 2> $_err_file
