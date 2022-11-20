#/bin/bash

. ./init.sh

#
# Read the id of the instance from the local config.py file
# by example dev, test or prod
#
#INSTANCE_ID=$(python $BASEDIR/cfgreader.py instance id)
INSTANCE_ID="prod"

#RESTAPI_UID=$1
#RESTAPI_PWD=$2

sudo mkdir -p /etc/iot_local_gw

#
# Create service
#
echo "... writing iot_gw.service ..."
cat << EOF | sudo tee /etc/systemd/system/iot_local_gw.$INSTANCE_ID.service
# do not change this file here!
# auto created by $BASEDIR/install.sh
[Unit]
Description=iot local site gw service
#After=syslog.target mysqld.service

[Service]
WorkingDirectory=$BASEDIR
#ExecStartPre=$VENV/bin/python smarthome-gw.py
ExecStart=$VENV/bin/python iot_local_gw.py

# Requires systemd version 211 or newer
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all
Type=idle

[Install]
WantedBy=multi-user.target
EOF

echo "...reloading systemctl ..."
sudo systemctl daemon-reload

echo "ready!"
