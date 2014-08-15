#!/bin/bash
DIR_NAME=$(date +%Y_%m%d_%H%M)
mkdir $DIR_NAME
mkdir $DIR_NAME/client_1_results/
mkdir $DIR_NAME/client_2_results/

# scp -i ec2_private_key ubuntu@$CSPARQL_OBSERVER_IP:~/results.txt $DIR_NAME/logs.txt
scp -i ec2_private_key ubuntu@$OFBIZ_CLIENT_1_IP:~/ofbench-client/results/test/response.csv $DIR_NAME/client_1_results/.
scp -i ec2_private_key ubuntu@$OFBIZ_CLIENT_2_IP:~/ofbench-client/results/test/response.csv $DIR_NAME/client_2_results/.

echo "Results directory: " $DIR_NAME

# path is relative to current working directory
# python ../parse_monitor_log.py $DIR_NAME

python
echo "Parsing results in directory: " $DIR_NAME