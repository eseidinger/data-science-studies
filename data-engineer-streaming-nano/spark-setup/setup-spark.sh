#!/bin/bash

mkdir /tmp/spark-events
sudo /usr/local/spark/sbin/start-history-server.sh
sudo cp spark-defaults.conf /usr/local/spark/conf/
