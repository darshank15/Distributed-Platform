#!/bin/bash
lb=$1
rmq=$2
host=$3
pip install -r requirements.txt
python LoadBalancer.py $rmq $host