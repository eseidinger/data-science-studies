#!/usr/bin/env bash

airflow initdb
airflow scheduler &
airflow "$1"
