## Squid Ipv6 Proxies

I made private ipv6 proxies for you. Use squid software. Translate ipv4 port to ipv6. Each port to one ipv6 outgoing

[toc]

## Features

* Single IP for each /64 subnet
* No Ipv4 leakage
* Anonymous, Elite, Transparent
* User/pass Authentication

## Requirements
- Python >= 3.6
- Squid v3
## Install

- `ubuntu_install.sh` This bash script used to rebuild squid. Default squid installs via the `apt` limit to 128 port. To make more proxies in squid, We need an increasing number of squid ports for proxy. Here, I change the number port listen to 65000
- `gen_squid.py`. This python script used to gen squid config

### Step 1

Run bash script

```bash
bash ubuntu_install.sh
```

This script will install dependency and clone this repo to /opt.

### Step 2
Gen Squid Config

To see usage:

```
PYTHONPATH=/opt/v6proxies python3.6 gen_squid.py --help 
```

Output

```
usage: gen_squid.py [-h] --ipv6_subnet_full IPV6_SUBNET_FULL --net_interface NET_INTERFACE --pool_name POOL_NAME [--username USERNAME] [--password PASSWORD] [--number_ipv6 NUMBER_IPV6] [--unique_ip UNIQUE_IP]
                    [--start_port START_PORT]

Gen Squid Config

optional arguments:
  -h, --help            show this help message and exit
  --ipv6_subnet_full IPV6_SUBNET_FULL
                        ipv6 subnet full
  --net_interface NET_INTERFACE
                        net interface
  --pool_name POOL_NAME
                        pool name
  --username USERNAME   username
  --password PASSWORD   password
  --number_ipv6 NUMBER_IPV6
                        number ipv6. Default = 250
  --unique_ip UNIQUE_IP
                        single ip for each /64 subnet. Default = 1
  --start_port START_PORT
                        start proxy port. Default 32000

```

For example. I have ipv6 subnet `2602:fed2:699b::/48` and I want to make `2000` proxies with start ipv4 port from `10000`, `each proxy on /64`

```shell script
PYTHONPATH=/opt/v6proxies python3.6 --ipv6_subnet_full 2602:fed2:699b::/48 --net_interface eth0 --pool_name squidv6  --number_ipv6 2000 --unique_ip 1 --start_port 10000
```
This script makes one squid config in /etc/squid with a filename like : `squid-squidv6.conf` and auth config file `squidv6.auth`

And one .sh like `add_ip_{pool_name}.sh` in /opt/v6proxies. In this example. file name is `add_ip_squidv6.sh`

`add_ip_{pool_name}.sh` is bash script to add ipv6 to network interface

To start proxies.

run two command

```shell script
bash /opt/v6proxies/add_ip_squidv6.sh
```

```shell script
/usr/local/squid/sbin/squid -f /etc/squid/squid-squidv6.conf
```

### Testing

```shell script
curl -x http://{user_name}:{password}@{IP}:{Port} https://ident.me 
```

example

```
curl -x http://cloud:v6ForYou69@127.0.0.1:10000 https://ident.me 
```

## License
Distributed under the MIT License. See `LICENSE` for more information.

 