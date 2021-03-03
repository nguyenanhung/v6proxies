# -*- coding: utf-8 -*-
import argparse
import os
import pathlib
from ipaddress import IPv6Network, IPv6Address
from random import seed, getrandbits, choices, choice

from passlib.apache import HtpasswdFile

parser = argparse.ArgumentParser(description='Gen Squid Config')
parser.add_argument('--ipv6_subnet_full', help='ipv6 subnet full', required=True)
parser.add_argument('--net_interface', help='net interface', required=True)
parser.add_argument('--pool_name', help='pool name', required=True)
parser.add_argument('--username', help='username', default='cloud')
parser.add_argument('--password', help='password', default='v6ForYou69')
parser.add_argument('--number_ipv6', help='number ipv6. Default = 250', default=250, type=int)
parser.add_argument('--unique_ip', help='single ip for each /64 subnet. Default = 1', default=1, type=int)
parser.add_argument('--start_port', help='start proxy port. Default 32000', default=32000, type=int)

args = parser.parse_args()

base_path = pathlib.Path(__file__).parent.absolute()

ipv6_subnet_full = args.ipv6_subnet_full
net_interface = args.net_interface
number_ipv6 = args.number_ipv6
unique_ip = args.unique_ip
start_port = args.start_port
pool_name = args.pool_name
username = args.username
password = args.password

sh_add_ip = f'add_ip_{pool_name}.sh'


def gen_ipv6(ipv6_subnet):
    seed()
    network = IPv6Network(ipv6_subnet)
    return IPv6Address(network.network_address + getrandbits(network.max_prefixlen - network.prefixlen))


def add_ipv6(num_ips, unique_ip=1):
    # if num_ips > 250:
    #     num_ips = 250
    list_ipv6 = []
    network2 = IPv6Network(ipv6_subnet_full)
    list_network2 = list(network2.subnets(new_prefix=64))

    if os.path.exists(path=sh_add_ip):
        os.remove(path=sh_add_ip)
        print("%s exists. Removed" % sh_add_ip)

    if unique_ip == 1:

        subnet = choices(list_network2, k=num_ips)

        for sub in subnet:
            ipv6 = gen_ipv6(ipv6_subnet=sub)
            list_ipv6.append(str(ipv6))

            cmd = f'ip -6 addr add {ipv6} dev {net_interface}'

            with open(sh_add_ip, 'a') as the_file:
                the_file.write(cmd + '\n')

    else:

        subnet = choices(list_network2, k=10)

        for i in range(0, num_ips):
            sub = choice(subnet)
            ipv6 = gen_ipv6(ipv6_subnet=sub)
            list_ipv6.append(str(ipv6))
            # print(ipv6)
            # r_conn.sadd(pool_name, ipv6)
            # cmd = '/sbin/ifconfig %s inet6 add %s/64' % (net_interface, ipv6)
            cmd = f'ip -6 addr add {ipv6} dev {net_interface}'
            with open(sh_add_ip, 'a') as the_file:
                the_file.write(cmd + '\n')
    return list_ipv6


cfg_squid = '''

    max_filedesc 500000
    pid_filename /usr/local/squid/var/run/{pid}.pid
    access_log          none
    cache_store_log     none

    # Hide client ip #
    forwarded_for delete

    # Turn off via header #
    via off

    # Deny request for original source of a request
    follow_x_forwarded_for allow localhost
    follow_x_forwarded_for deny all

    # See below
    request_header_access X-Forwarded-For deny all

    request_header_access Authorization allow all
    request_header_access Proxy-Authorization allow all
    request_header_access Cache-Control allow all
    request_header_access Content-Length allow all
    request_header_access Content-Type allow all
    request_header_access Date allow all
    request_header_access Host allow all
    request_header_access If-Modified-Since allow all
    request_header_access Pragma allow all
    request_header_access Accept allow all
    request_header_access Accept-Charset allow all
    request_header_access Accept-Encoding allow all
    request_header_access Accept-Language allow all
    request_header_access Connection allow all
    request_header_access All deny all

    cache           deny    all

    acl to_ipv6 dst ipv6
    http_access deny all !to_ipv6
    acl allow_net src 1.1.1.1
    {squid_conf_suffix}
    {squid_conf_refresh}
    {block_proxies}
'''

squid_conf_refresh = '''
  refresh_pattern ^ftp:       1440    20% 10080
    refresh_pattern ^gopher:    1440    0%  1440
    refresh_pattern -i (/cgi-bin/|\?) 0 0%  0
    refresh_pattern .       0   20% 4320
'''

squid_conf_suffix = '''
 # Common settings
    acl SSL_ports port 443
    acl Safe_ports port 80      # http
    acl Safe_ports port 21      # ftp
    acl Safe_ports port 443     # https
    acl Safe_ports port 70      # gopher
    acl Safe_ports port 210     # wais
    acl Safe_ports port 1025-65535  # unregistered ports
    acl Safe_ports port 280     # http-mgmt
    acl Safe_ports port 488     # gss-http
    acl Safe_ports port 591     # filemaker
    acl Safe_ports port 777     # multiling http
    acl CONNECT method CONNECT

    http_access deny !Safe_ports

    http_access deny CONNECT !SSL_ports

    http_access allow localhost manager
    http_access deny manager

    auth_param basic program /usr/local/squid/libexec/basic_ncsa_auth /etc/squid/{pid}.auth

    auth_param basic children 5
    auth_param basic realm Web-Proxy
    auth_param basic credentialsttl 1 minute
    auth_param basic casesensitive off

    acl db-auth proxy_auth REQUIRED
    http_access allow db-auth
    http_access allow localhost
    http_access deny all


    coredump_dir /var/spool/squid3
    unique_hostname V6proxies-Net
    visible_hostname V6proxies-Net
'''

proxies = ''''''
ipv6 = add_ipv6(num_ips=number_ipv6, unique_ip=unique_ip)

for ip_out in ipv6:
    proxy_format = '''
    http_access allow allow_net
    http_port       {port}
    acl     p{port}  localport       {port}
    tcp_outgoing_address    {ip_out} p{port}
    '''.format(port=start_port, ip_out=ip_out)
    start_port = start_port + 1
    proxies += proxy_format + '\n'

auth_file = f'/etc/squid/{pool_name}.auth'

ht = HtpasswdFile(auth_file, new=True)
ht.set_password(username, password)
ht.save()

cfg_squid_gen = cfg_squid.format(pid=pool_name, squid_conf_refresh=squid_conf_refresh,
                                 squid_conf_suffix=squid_conf_suffix.format(pid=pool_name),
                                 block_proxies=proxies)

squid_conf_file = f'/etc/squid/squid-{pool_name}.conf'
if os.path.exists(path=squid_conf_file):
    os.remove(path=squid_conf_file)
    print("%s exists. Removed" % squid_conf_file)
with open(squid_conf_file, 'a') as the_file:
    the_file.write(cfg_squid_gen + '\n')

print("=========================== \n")
print("\n \n")
print("Run two command bellow to start proxies")
print("\n \n")
print(f"bash {base_path}/{sh_add_ip}")
print(f"/usr/local/squid/sbin/squid -f {squid_conf_file}")
print("\n \n")
print("Create %d proxies. Port start from %d with user: %s | password: %s" % (
    number_ipv6, start_port, username, password))