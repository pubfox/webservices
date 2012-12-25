import time
import os
import re
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
    