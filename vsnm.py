#!/usr/bin/env python2

import ConfigParser, os, re

def init_wireless(dev):
    os.system('ip link set ' + dev + ' down')
    os.system("rfkill unblock wifi")
    os.system('killall -9 dhclient')
    os.system('killall -9 wpa_supplicant')
    os.system('ip link set ' + dev + ' up')
    os.system('sleep 1')

def connect_wep(dev, ssid):
    os.system("ifconfig " + dev + " down")
    os.system("iwconfig " + dev + " essid '" + ssid + "'")
    os.system("iwconfig " + dev + " ap any")
    os.system('ip link set ' + dev + ' up')

def connect_wpa(dev, ssid, psk):
    os.system("wpa_passphrase " + ssid  + " " + psk + " > /etc/wpa_supplicant/wpa_supplicant.conf")
    os.system("wpa_supplicant -d -Dwext  -i " + dev + " -c /etc/wpa_supplicant/wpa_supplicant.conf >& log.txt &")
    os.system("sleep 5")

def set_dns(dns1, dns2):
    fd = open('/etc/resolv.conf', 'w')
    fd.write('nameserver ' + dns1 + '\n')
    fd.write('nameserver ' + dns2 + '\n')
    fd.close()


config = ConfigParser.ConfigParser()
config.readfp(open('/etc/vsnm.cfg'))

dev = config.get('global', 'dev');
init_wireless(dev)

p = os.popen('iwlist ' + dev + ' scan');
ssid_list = []
while 1:
    line = p.readline()
    if not line:
        break;
    if line.find("ESSID") != -1:
        line = re.sub("^.*ESSID:", "", line)
        line = re.sub('"', '', line)
        line = line.replace('\n', '')
        ssid_list.append(line)
        print(line)


for entry in config.sections():
    if entry != 'global':
        ssid = config.get(entry, 'ssid')
        try:
            i = ssid_list.index(ssid)
        except ValueError:
            continue

        protocol = config.get(entry, 'protocol')

        if 'WEP' == protocol:
            connect_wep(dev, ssid)
        elif 'WPA' == protocol:
            psk = config.get(entry, 'psk')
            print("ssid: " + ssid)
            print("psk: " + psk)
            connect_wpa(dev, ssid, psk)
        else:
            print("ERROR: protocol not recognized")

	net = config.get(entry, 'net')
	if 'dhcp' == net:
	    os.system("dhclient " + dev)
	elif 'static' == net:
	    address = config.get(entry, 'address')
	    os.system("ifconfig " + dev + " " + address)
	    try:
		os.system("sh " + config.get(entry, 'post-script'))
	    except ConfigParser.NoOptionError:
		continue
		

        set_dns(config.get('global', 'dns1'), config.get('global', 'dns2'))

        break;
