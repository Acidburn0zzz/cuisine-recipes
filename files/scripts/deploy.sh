#!/bin/bash

########################################################################
#
# This script will deploy a new version of MY APP in PROD.
#
# Change the access rights:
# $ sudo chmod 700 deploy.sh
#
########################################################################

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

echo "`date "+%Y-%m-%d %H:%M:%S"` Deploying app..."

echo "Stopping PROD..."
service tomcat7 stop

cd /home/ubuntu/webapps/ROOT

echo "Cleaning webapps folder..."
rm -rf /home/ubuntu/webapps/ROOT/*

echo "Unpacking application..."
#tar xzf /home/ubuntu/myapp.tgz
unzip /home/ubuntu/myapp-0.1.war

echo "Setting permissions..."
chown -R tomcat7:tomcat7 /home/ubuntu/webapps/ROOT
chmod -R 770 /home/ubuntu/webapps/ROOT

echo "Restarting PROD..."
service /tomcat7 start