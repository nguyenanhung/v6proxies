#!/usr/bin/env bash


# install repo
echo "=========== Install Repo ================="
apt update && apt upgrade -y

echo "==========================================="

# install depend
echo "=========== Install Depend ================="

apt install build-essential vim git wget htop curl python3.8 python3.8-dev python3.8-venv python3-pip -y
pip3 install pip --upgrade


echo "==========================================="

# build squid

echo "=========== reBuild Squid ================="

cd /opt
wget -c http://www.squid-cache.org/Versions/v3/3.5/squid-3.5.27.tar.gz
tar -zxvf squid-3.5.27.tar.gz
cd squid-3.5.27
./configure 'CXXFLAGS=-DMAXTCPLISTENPORTS=65000' --enable-ltdl-convenience
make && make install
chmod 777 /usr/local/squid/var/logs/
mkdir /var/spool/squid3
mkdir /etc/squid

echo "==========================================="


echo "=========== Install Python requirements ================="
cd /opt/
git clone https://github.com/nguyenanhung/v6proxies.git
cd /opt/v6proxies
pip3.8 install --upgrade pip setuptools
pip3.8 install -r requirements.txt

# Increase The Maximum Number Of Open Files

echo "* - nofile 500000" >> /etc/security/limits.conf

echo "=========== Init ================="
