SCRIPTNAME=$BASH_SOURCE
BASEDIR=$(realpath $SCRIPTNAME)
BASEDIR=$(dirname $BASEDIR)
cd $BASEDIR

. ./init.sh
#python tuya_scan.py
python smarthome-gw.py

