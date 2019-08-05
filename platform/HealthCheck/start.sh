#!/bin/bash
lb=$1
rmq=$2
host=$3
pip install -r requirements.txt
python HealthCheck.py $lb $rmq $host