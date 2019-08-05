#!/bin/bash
echo 'Executing ...'
username=$1
password=$2
mount_ip=$3
mount_path=$4
ip=$5
lb=$6
if mount | grep /nfs > /dev/null; then
    echo "NFS is mounted"
else
    echo "Not mounted"
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' nfs-common |grep "install ok installed")
    echo $PKG_OK
    if [ "install ok installed" == "$PKG_OK" ]; then
        echo 'NFS COMMON IS INSTALLED'
    else
        echo 'NFS COMMON IS NOT INSTALLED'
        echo "$password" | sudo -S apt-get install nfs-common -y
    fi
    echo "$password" | sudo -S mkdir -p /nfs/home > /dev/null

    echo "$password" | sudo -S mount $mount_ip:$mount_path /nfs/home
    
fi

echo "hello"
count=$(ps aux | grep server_stats.py | wc -l)
if [ $count -ge 2 ]; then
    echo 'Running'
else
    echo "Not running"
    echo "$password" | sudo -S cp -r /nfs/home/ServerStatsModule .
    cd ServerStatsModule
    python server_stats.py $ip &>/dev/null &
    cd ..
    echo 'Server stats started'
fi

count=$(ps aux | grep start_docker_service.py | wc -l)
if [ $count -ge 2 ]; then
    echo 'Running'
else
    echo "Not running"
    echo "$password" | sudo -S cp -r /nfs/home/MachineAgent .
    cd MachineAgent
    python start_docker_service.py $lb $ip &>/dev/null &
    cd ..
    echo 'Start Docker Service Started'
fi

#echo "$password" | sudo -S cp -r /nfs/home/ServerStatsModule .
#cd ServerStatsModule
#python server_stats.py 'localhost' &>/dev/null &
#cd ..
#echo 'Server stats started'