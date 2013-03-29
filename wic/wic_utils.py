import time
import os
import re
import netaddr
from wic_client_defines import *

def get_timestamp():
    return time.strftime(ISOTIMEFORMAT, time.localtime())

def get_hostmap(hosts):
    file = "/etc/hosts"
    if not os.path.isfile(file): return None
    fp = open(file, "r")
    for line in fp.readlines():
        if re.search(r'^$', line) or not re.match(r'\d', line) : continue
        if line.split()[0] not in ["localhost", "127.0.0.1"]:
            hosts[line.split()[1]] = line.split()[0]
    return len(hosts)

def get_img_name(name):
    if not re.search('_', name): return name
    return "".join( name.split('_')[0] )

def get_ins_hostname(ins_id, ins_list):
    for ins in ins_list:
        if ins["id"] == ins_id:
            return ins["host"]

def get_ins_hostip(ins_id, ins_list, host_map):
    hostname = None
    for ins in ins_list:
        if ins["id"] == ins_id:
            hostname = ins["host"]
            break
    if not hostname or not host_map.has_key(hostname): return None
    return host_map[hostname]
    
def gb_to_mb(gb):
    '''if  type(gb) != type(1.0) and str(gb) != "0.5":
        print "err here"
        return -1'''
    return float(gb) * 1024 

def get_device_location(ins_id):
    ins_vol = {}
    fp = open(attach_file, "r")
    for line in fp.readlines():
        if len(line) > 1:
            if ins_vol.has_key(line.split()[1]):
                ins_vol[line.split()[1]] = char_max(ins_vol[line.split()[1]], line.split()[2][-1])
            else:
                ins_vol[line.split()[1]] = line.split()[2][-1]
    fp.close()
    if not ins_vol.has_key(ins_id):
        return "/dev/vdc"
    return "/dev/vd" + chr(ord(ins_vol[ins_id]) + 1)

def char_max(a, b):
    if a > b:
        return
    else: return b
    
def write_device_location(ins_id, volume_id, device):
    fp = open(attach_file, "a")
    fp.writelines(str(volume_id) + " " + str(ins_id) + " " + str(device) + "\n")
    fp.close()
    
def delete_device_location(ins_id, volume_id):
    cmd = "sed -i '/^" + str(volume_id) + ".*" + str(ins_id) + "/d' " + attach_file
    print cmd
    os.system(cmd)
    
def iprange_to_cidrs(iprange):
    ip_start, ip_end = iprange.split("-")
    try:
        cidrs = netaddr.iprange_to_cidrs(ip_start, ip_end)
    except Exception, ex:
        return WIC_RES_FAILED, None
    return WIC_RES_SUCCESS, cidrs

def get_secgroup_id(secgroup_name, content):
    for group in content["security_groups"]:
        if group["name"] == secgroup_name:
            return group["id"]
    return None

def get_secgroup_rule_id(content, protocol, from_port, 
                         to_port, parent_group_id, group = None, ip_range = None):
    for group in content["security_groups"]:
        if group["rules"]:
            for rule in group["rules"]:
                if rule["parent_group_id"] == int(parent_group_id) and \
                rule["from_port"] == int(from_port) and rule["to_port"] == int(to_port):
                    print rule