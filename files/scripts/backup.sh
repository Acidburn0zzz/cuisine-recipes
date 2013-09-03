#!/bin/bash

FILEPATH=/home/ubuntu/backups/
FILE=backup-alldb-`date +"%Y-%m-%d"`.sql.gz
mysqldump --all-databases -u root --proot_password | gzip > $FILEPATH$FILE

# Copy file to S3
