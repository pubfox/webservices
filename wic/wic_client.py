#!/usr/bin/python

import httplib2
import json
import sys
import time
import subprocess
import re
import os
import urllib2
import wic_utils
import threading
import logging
from urlparse import urlparse
from wic_client_defines import *
import wic_format
from novaclient.v1_1.client import Client
import novaclient
#from wic_floating import *
#from nova import flags
#from nova import log as logging

#FLAGS = flags.FLAGS

#LOG = logging.getLogger(__name__)

class Base(object):
    def __init__(self, tenant = default_tenant):
        body = {
                       "auth": {
                          "passwordCredentials": {"username": osuser,
                                                  "password": ospassword}
                                }
                       }
        body['auth']['tenantName'] = tenant
        body = json.dumps(body)
        headers = {
                                'Content-Type': 'application/json', 
                                'Accept': 'application/json', 
                                'User-Agent': 'client'
                  }
        http = httplib2.Http()
        resp, body = http.request (token_uri, method = "POST", body=body, headers=headers)
        if not resp.status == 200:
            print "Error status: %d" % resp.status
            sys.exit(1)
        data = json.loads(body)
        self.apitoken = data['access']['token']['id']
        self.volumeurl = data['access']['serviceCatalog'][0]['endpoints'][0]['publicURL']
        self.apiurl = data['access']['serviceCatalog'][2]['endpoints'][0]['publicURL']
        self.tenant_id = data['access']['token']['tenant']['id']
        self.headers =  {
                                    'X-Auth-Project-Id' : tenant,
                                    'User-Agent' : 'python-novaclient',
                                    'Content-Type' : 'application/json',
                                    'Accept' : 'application/json',
                                    'X-Auth-Token' : self.apitoken
                         }
        self.key_uri = key_uri
        self.host_map = {}
        self.img_dict = {}
        self.ins_list = []
        self.flavor_ls = []
        self.host_len = wic_utils.get_hostmap(self.host_map)
        self.client = Client(osuser, ospassword, default_tenant, auth_uri)
        
    def flavor_list(self):
        uri = self.apiurl + "/flavors/detail"
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        if resp.status == 200:
            data = json.loads(content)
            #print data
            self.flavor_ls = data["flavors"]
            return len(self.flavor_ls)
        return None
    
    def flavor_find(self, id = None, vcpu = None, ram = None):
        print vcpu
        print ram
        if id: 
            for fl in self.flavor_ls:
                if fl["id"] == str(id):
                    return fl["links"][0]["href"], id
        for fl in self.flavor_ls:
            if fl["vcpus"] == int(vcpu) and fl["ram"] == int(ram):
                return fl["links"][0]["href"], fl['id']
        raise "not found flavor"
        return None
            
    def img_list(self):
        uri = self.apiurl + "/images"
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        data = json.loads(content)
        for i in range(len(data['images'])):
            self.img_dict[ str(data["images"][i]["id"]) ] = str(data["images"][i]["name"])
        return len(self.img_dict)
    
    def find_image(self, image_type):
        len = self.img_list()
        if not len: return None
        for k, v in self.img_dict.items():
            if v == str(image_type):
                return k
        return None
    
    def guest_list(self):
        img_len = self.img_list()
        uri = self.apiurl + "/servers/detail"
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        data = json.loads(content)
        for i in range(len(data["servers"])):
            self.instance_dict = {}
            self.instance_dict["id"] = str( data["servers"][i]["id"] )
            self.instance_dict["name"] = str( data["servers"][i]["name"] )
            self.instance_dict["status"] = str( data["servers"][i]["status"] )
            self.instance_dict["flavor"] = str( data["servers"][i]["flavor"]["id"] )
            self.instance_dict["host"] = str( data["servers"][i]["OS-EXT-SRV-ATTR:host"] )
            self.instance_dict["home"] = self.host_map[ self.instance_dict["host"] ]
            if data["servers"][i]["addresses"].has_key("private"):
                self.instance_dict["addr"] = str( data["servers"][i]["addresses"]["private"][0]["addr"] )
            else: self.instance_dict["addr"] = None
            self.instance_dict["imageid"] = str( data["servers"][i]["image"]["id"] )
            self.instance_dict["img"] = wic_utils.get_img_name( self.img_dict[ self.instance_dict["imageid"] ] )
            self.ins_list.append(self.instance_dict)
        return len(self.ins_list)
    
    def add_user(self, username, password, email, tenantId):
        uri = self.key_uri + "/users"
        self.key_headers = {'User-Agent': 'python-keystoneclient', 
                            'Content-Type': 'application/json', 
                            'X-Auth-Token': 'ADMIN'}
        
        body = {
                "user": 
                    {
                     "email": email, 
                     "password": password, 
                     "enabled": True, 
                     "name": username, 
                     "tenantId": tenantId
                     }
                }
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request (uri, method = "POST", headers=self.key_headers, body = body)
        if resp.status == 200:
            data = json.loads(content)
            userId = data["user"]["id"]
            return WIC_RES_SUCCESS, userId
        return WIC_RES_FAILED, None
    
    def instance_create(self, request_id, image_id, flavor_id, security_groups=default_sec, key_name = default_keypair):
        instance_name = "ins_" + str(request_id)
        '''
        uri = self.apiurl + "/servers"
        body = {
                        "server" : {
                                        "name" : instance_name,
                                        "imageRef" : image_ref,
                                        "key_name" : key_name,
                                        "flavorRef" : flavor_ref,
                                        "max_count" : default_max_count,
                                        "min_count" : default_min_count,
                                   }
                       }
        if security_group:
            body['server']["security-groups"] = [security_group]
        body = json.dumps(body)
        print body
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        print resp, content
        if resp.status != 200 and resp.status != 202:
            return WIC_RES_FAILED , None
        data = json.loads(content)
        ins_id = data["server"]["id"]
        print ins_id
        '''
        try:
            image = self.client.images.get(image_id)
            flavor = self.client.flavors.get(flavor_id)
            security_groups = [] if not security_groups else [security_groups]
            res = self.client.servers.create(instance_name, image, flavor, security_groups=security_groups, key_name=key_name)
            return WIC_RES_SUCCESS, res.id
        except:
            return WIC_RES_FAILED , None 
    
    def instance_show(self, ins_id):
        uri = self.apiurl + "/servers/" + str(ins_id)
        http = httplib2.Http()
        try:
            resp, content = http.request (uri, method = "GET", headers=self.headers)
        except Exception, ex:
            return WIC_RES_FAILED, None
        if resp.status != 200 and resp.status != 202: return WIC_RES_FAILED, None
        data = json.loads(content)
        return WIC_RES_SUCCESS, data["server"]["status"]
    
    def instance_info(self, ins_id):
        uri = self.apiurl + "/servers/" + str(ins_id)
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        if resp.status != 200 and resp.status != 202: return WIC_RES_FAILED
        data = json.loads(content)
        return WIC_RES_SUCCESS, data
    
    def _secgroup_show(self):
        uri = self.apiurl + str('/os-security-groups')
        print uri
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        return json.loads(content)
    
    def secgroup_create(self, secgroup_name):
        uri = self.apiurl + str('/os-security-groups')
        print secgroup_name
        body = {"security_group": {"name": secgroup_name, "description": default_sec_desc}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request (uri, method = "POST", body = body, headers=self.headers)
        print resp, content
        if resp.status == 200:
            data = json.loads(content)
            return WIC_RES_SUCCESS, data["security_group"]["id"]
        return WIC_RES_FAILED, None
    
    def secgroup_delete(self, secgroup_id):
        uri = self.apiurl + str('/os-security-groups/') + str(secgroup_id)
        http = httplib2.Http()
        resp, content = http.request (uri, method = "DELETE", headers=self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def secgroup_show(self):
        uri = self.apiurl + str('/os-security-groups')
        http = httplib2.Http()
        try:
            resp, content = http.request (uri, method = "GET", headers=self.headers)
        except Exception, e:
            return WIC_RES_FAILED, None
        content = json.loads(content)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS, content
        return WIC_RES_FAILED, None
    
    def secgroup_add_rule(self, protocol, from_port, to_port, parent_group_id, group = None, ip_range = None):
        if ip_range:
            res, cidrs = wic_utils.iprange_to_cidrs(ip_range)
            if res == WIC_RES_FAILED:
                return res
            for cidr in cidrs:
                res += self.do_secgroup_add_rule(protocol, from_port, to_port, parent_group_id, cidr = str(cidr))
                time.sleep(1)
            if res > WIC_RES_SUCCESS:
                return WIC_RES_FAILED
            else: return res
        elif group:
            res = self.do_secgroup_add_rule(protocol, from_port, to_port, parent_group_id, group = int(group))
            return res
    
    def do_secgroup_add_rule(self, protocol, from_port, to_port, parent_group_id, group = None, cidr = None):
        uri = self.apiurl + str('/os-security-group-rules')
        body = {
                "security_group_rule": 
                {"from_port": str(from_port), "ip_protocol": str(protocol), 
                 "to_port": str(to_port), "parent_group_id": int(parent_group_id)}
                }
        if cidr:
            body["security_group_rule"]["cidr"] = cidr
        if group:
            body["security_group_rule"]["group_id"] = int(group)
        body = json.dumps(body)
        print body
        http = httplib2.Http()
        resp, content = http.request (uri, method = "POST", body = body, headers=self.headers)
        print resp
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def secgroup_delete_rule(self, content, protocol, from_port, to_port,
                              parent_group_id, group = None, ip_range = None):
        if group:
            id = wic_utils.get_secgroup_rule_id(content, protocol, from_port, 
                                                to_port, parent_group_id, group = group)
        elif ip_range:
            id = wic_utils.get_secgroup_rule_id(content, protocol, from_port, 
                                                to_port, parent_group_id, ip_range = ip_range)
    
    def do_secgroup_delete_rule(self, rule_id):
        uri = self.apiurl + str('/os-security-group-rules/') + str(rule_id)
        http = httplib2.Http()
        resp, content = http.request (uri, method = "DELETE", headers=self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
                
    def instance_suspend(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"suspend" : None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        print resp, content
        if resp.status in [200, 202]:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def instance_delete(self, ins_id):
        uri = self.apiurl + "/servers/" + str(ins_id)
        http = httplib2.Http()
        try:
            resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        except Exception, e:
            return WIC_RES_FAILED
        if resp.status == 200 or resp.status == 202 or resp.status == 204:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def volume_create(self, size):
        uri  = self.volumeurl + "/volumes"
        body = {
                    "volume": 
                        {
                         "snapshot_id": None,
                         "display_name": None, 
                         "volume_type": None, 
                         "display_description": None, 
                         "size": size
                        }
                }
        body = json.dumps (body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        #print resp, content
        if resp.status == 200:
            data = json.loads(content)
            volume_id = data["volume"]["id"]
            return WIC_RES_SUCCESS, volume_id
        return WIC_RES_FAILED, None
    
    def volume_attach(self, ins_id, volume_id, device = '/dev/vde'):
        uri = self.apiurl + "/servers/" + ins_id + "/os-volume_attachments"
        body = {
                    "volumeAttachment": 
                        {
                         "device": device, 
                         "volumeId": volume_id
                        }
                }
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        #print resp, content
        if resp.status == 200 or resp.status == 202:
            self.instance_reboot(ins_id)
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def volume_dettach(self, ins_id, volume_id):
        uri = self.apiurl + "/servers/" + str(ins_id) + "/os-volume_attachments/" + str(volume_id)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def volume_delete(self, volume_id):
        uri = self.volumeurl + "/volumes/" + str(volume_id)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def volume_show(self, volume_id):
        ins_id = None
        uri = self.volumeurl + "/volumes/" + str(volume_id)
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        if resp.status != 200 and resp.status != 202:
            print "return" 
            return WIC_RES_FAILED, None, ins_id
        data = json.loads(content)
        if data["volume"]["status"] == "in-use":
            ins_id = data["volume"]["attachments"][0]["server_id"]
        return WIC_RES_SUCCESS, data["volume"]["status"], ins_id
    
    def instance_reboot(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"reboot": {"type": "SOFT"}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def instance_pause(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"pause" : None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200 or resp.status == 202 or resp.status == 204:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def instance_unpause(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"unpause" : None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200 or resp.status == 202 or resp.status == 204:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def floating_ip_create(self):
        uri = self.apiurl + '/os-floating-ips'
        body = {"pool": None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        content = json.loads(content)
        if resp.status == 200:
            return WIC_RES_SUCCESS, content["floating_ip"]["ip"]
        return WIC_RES_FAILED, None
    
    def floating_ip_delete(self, ipaddr):
        uri = self.apiurl + '/os-floating-ips'
        id = None
        http = httplib2.Http()
        resp, content = http.request(uri, method = "GET", headers = self.headers)
        if resp.status != 200:
            return WIC_RES_FAILED
        data = json.loads(content)
        for floating_ip in data["floating_ips"]:
            if floating_ip["ip"] == ipaddr:
                id = floating_ip["id"]
                break
        if not id: return WIC_RES_FAILED
        uri = self.apiurl + '/os-floating-ips/' + str(id)
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200: return WIC_RES_SUCCESS
        return WIC_RES_FAILED
            
    
    def floating_ip_add(self, ins_id, ipaddr):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        print uri
        print ipaddr
        body = {"addFloatingIp": {"address": ipaddr}}
        body = json.dumps(body)
        print self.headers
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        print content
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS, default_note
        return WIC_RES_FAILED, 'BindIp error, please check instanceId, ip'
    
    def floating_ip_remove(self, ins_id, ipaddr):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"removeFloatingIp": {"address": str(ipaddr)}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def netspeed_update(self, ins_id, netspeed):
        ins_len = self.guest_list()
        if not ins_len: return WIC_RES_FAILED
        hostip = wic_utils.get_ins_hostip(ins_id, self.ins_list, self.host_map)
        if not hostip:
            return WIC_RES_FAILED, None
        uri = "http://" + str(hostip) + ":" + DEV_CTL_PORT + "/instance_device/netspeed/" + str(ins_id) + "/0"
        req = urllib2.Request(uri)
        fd = urllib2.urlopen(req)
        ret = fd.read(3)
        if ret == "nok":
            return WIC_RES_FAILED, hostip
        uri = "http://" + str(hostip) + ":" + DEV_CTL_PORT + "/instance_device/netspeed/" + str(ins_id) + "/" + str(netspeed)
        print uri
        req = urllib2.Request(uri)
        fd = urllib2.urlopen(req)
        ret = fd.read(3)
        print ret
        if ret == "nok":
            return WIC_RES_FAILED, hostip  
        return WIC_RES_SUCCESS, hostip
    
    def volume_snapshot_create(self, volume_id):
        uri = self.volumeurl + "/snapshots"
        body = {"snapshot": {"display_name": None, "force": False, "display_description": None, "volume_id": volume_id}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200 or resp.status == 202:
            data = json.loads(content)
            return WIC_RES_SUCCESS, str(data["snapshot"]["id"])
        return WIC_RES_FAILED, None
    
    def volume_snapshot_delete(self, snapshot_id):
        uri = self.volumeurl + "/snapshots/" + str(snapshot_id)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200 or resp.status == 202:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
        
class wic_client(Base):
    def __init__(self, tenant = default_tenant):
        super(wic_client, self).__init__()
    
    def CreateUser(self, *args, **kwargs):
        if not kwargs["CreateUser"]["userName"]: return WIC_RES_FAILED
        username = kwargs["CreateUser"]["userName"]
        if not "instanceId" in kwargs["CreateUser"].keys():
            kwargs["CreateUser"]["password"] = default_password
        password = kwargs["CreateUser"]["password"]
        if not kwargs.has_key("email"):
            kwargs["CreateUser"]["email"] = default_email
        email = kwargs["CreateUser"]["email"]
        tenantId = self.tenant_id
        kwargs["CreateUser"]["timestamp"] = wic_utils.get_timestamp()
        status, userId = self.add_user(username, password, email, tenantId)
        kwargs["CreateUser"]["userId"] = userId
        return kwargs
    
    def Create(self, **kwargs):
        flavor_id = kwargs["Create"]["CreateHost"]["hostSpecId"]
        group_name = kwargs["Create"]["CreateHost"]["groupName"]
        os_name = kwargs["Create"]["CreateHost"]["os"]
        netspeed = kwargs["Create"]["CreateIp"]["netSpeed"]
        disk = kwargs["Create"]["CreateDisk"]["disk"]
        request_id = kwargs["requestId"]
        kwargs = wic_format.make_default_create_response(kwargs)
        ram = wic_utils.gb_to_mb(kwargs["Create"]["CreateHost"]["memory"])
        if group_name:
            try:
                self.client.security_groups.find(name=group_name)
            except:
                kwargs["Create"]["CreateHost"]["result"] == WIC_RES_FAILED
                kwargs["Create"]["CreateHost"]["note"] = "groupName not found"
                return kwargs
        if ram == -1:
            kwargs["Create"]["CreateHost"]["result"] == WIC_RES_FAILED
            kwargs["Create"]["CreateHost"]["note"] = "memory format error"
            return kwargs
        
        n = self.flavor_list()
        #print "core:", kwargs["Create"]["CreateHost"]["core"]
        #print "ram:", ram
        if not flavor_id:
            try:
                flavor_ref, flavor_id = self.flavor_find(vcpu = str(kwargs["Create"]["CreateHost"]["core"]), \
                                          ram = float(ram))
            except:
                kwargs["Create"]["CreateHost"]["note"] = "can't find suitable core, memory"
                kwargs["Create"]["CreateHost"]["result"] = WIC_RES_FAILED
                return kwargs
        else:
            try:
                flavor_ref, flavor_id = self.flavor_find(id = flavor_id)
            except:
                kwargs["Create"]["CreateHost"]["note"] = "can't find suitable hostSpecId"
                kwargs["Create"]["CreateHost"]["result"] = WIC_RES_FAILED
                return kwargs
        #flavor_ref = self.flavor_find(id = flavor_id)
        image_id = self.find_image(os_name)
        if not image_id:
            kwargs["Create"]["CreateHost"]["result"] = WIC_RES_FAILED
            kwargs["Create"]["CreateHost"]["note"] = 'os not found'
            return kwargs
        image_ref = self.apiurl + "/images/" + str(image_id)
        res, ins_id = self.instance_create(request_id, image_id, flavor_id, group_name)
        kwargs["Create"]["CreateHost"]["result"] = res
        kwargs["Create"]["CreateHost"]["instanceId"] = ins_id
        kwargs["Create"]["CreateHost"]["imageId"] = image_id
        kwargs["Create"]["CreateHost"]["instanceType"] = flavor_id
        kwargs["Create"]["CreateHost"]["kernelId"] = os_name
        kwargs["Create"]["CreateHost"]["vpcId"] = 0
        kwargs["Create"]["CreateHost"]["rateLimit"] = netspeed
        if disk != None:
            disk_thread = threading.Thread(target = self.asynchronous_createDisk, args = (disk, ins_id))
            disk_thread.start()
        if netspeed != None:
            net_thread = threading.Thread(target = self.asynchronous_netspeed, args = (netspeed, ins_id))
            net_thread.start()
        return kwargs
    
    def asynchronous_createDisk(self, size, ins_id):
        res, volume_id = self.volume_create(size)
        if res == WIC_RES_FAILED: return res
        res = self.waiting_ins_ready(ins_id)
        if res == WIC_RES_FAILED: return res
        res = self.volume_attach(ins_id, volume_id, device = "/dev/vdx")
        return res
    
    def asynchronous_netspeed(self, netspeed, ins_id):
        res = self.waiting_ins_ready(ins_id)
        if res == WIC_RES_FAILED: return
        res, hostip = self.netspeed_update(ins_id, netspeed)
        return res
    
    def waiting_ins_ready(self, ins_id):
        try_times = 0
        while try_times < default_try_times:
            res, status = self.instance_show(ins_id)
            if status == 'ACTIVE': return WIC_RES_SUCCESS
            try_times += 1
            time.sleep(default_sleep_time)
        print "waiting_ins_ready timeout"
        return WIC_RES_FAILED
    
    def waiting_volume_attached(self, volume_id):
        try_times = 0
        while try_times < default_try_times:
            res, status, ins_id = self.volume_show(volume_id)
            if str(status) == "in-use": return WIC_RES_SUCCESS
            try_times += 1
            time.sleep(default_sleep_time)
        return WIC_RES_FAILED
    
    def waiting_volume_detached(self, volume_id):
        try_times = 0
        while try_times < default_try_times:
            res, status, ins_id = self.volume_show(volume_id)
            if str(status) == "available": return WIC_RES_SUCCESS
            try_times += 1
            time.sleep(default_sleep_time)
        return WIC_RES_FAILED
    
    def auto_volume_attach(self, ins_id, volume_id):
        device = wic_utils.get_device_location(ins_id)
        print device
        if not device:
            return WIC_RES_FAILED
        res = self.volume_attach(ins_id, volume_id, device = device)
        if res == WIC_RES_SUCCESS:
            wic_utils.write_device_location(ins_id, volume_id, device)
        return res
        
    def CreateSecurityGroup(self, **kwargs):
        kwargs["CreateSecurityGroup"]["note"] = default_note
        if not kwargs["CreateSecurityGroup"]["groupName"]:
            kwargs["CreateSecurityGroup"]["result"] = WIC_RES_FAILED
            kwargs["CreateSecurityGroup"]["note"] = "groupName can't be blank"
            return kwargs
        secgroup_name = kwargs["CreateSecurityGroup"]["groupName"]
        all_secgroups = self._secgroup_show()
        for secgroup in all_secgroups['security_groups']:
            if secgroup['name'] == secgroup_name:
                kwargs["CreateSecurityGroup"]["result"] = WIC_RES_FAILED
                kwargs["CreateSecurityGroup"]["note"] = "groupName already exists"
                return kwargs
        kwargs["CreateSecurityGroup"]["result"], id = self.secgroup_create(secgroup_name)
        return kwargs
        
    def DescribeSecurityGroup(self, *args, **kwargs):
        kwargs["DescribeSecurityGroup"]["note"] = default_note
        kwargs["DescribeSecurityGroup"]["timestamp"] = wic_utils.get_timestamp()
        secgroup_name = kwargs["DescribeSecurityGroup"]["groupName"]
        all_secgroups = self._secgroup_show()
        for secgroup in all_secgroups['security_groups']:
            if secgroup['name'] == secgroup_name:
                kwargs["DescribeSecurityGroup"]["result"] = WIC_RES_SUCCESS
                return kwargs
        kwargs["DescribeSecurityGroup"]["note"] = 'groupName not found'
        kwargs["DescribeSecurityGroup"]["result"] = WIC_RES_FAILED
        return kwargs
    
    def DelSecurityGroup(self, **kwargs):
        kwargs["DelSecurityGroup"]["note"] = default_note
        kwargs["DelSecurityGroup"]["timestamp"] = wic_utils.get_timestamp()
        secgroup_name = kwargs["DelSecurityGroup"]["groupName"]
        all_secgroups = self._secgroup_show()
        for secgroup in all_secgroups['security_groups']:
            if secgroup['name'] == secgroup_name:
                secgroup_id = secgroup['id']
                try:
                    self.client.security_groups.delete(secgroup_id)
                    kwargs["DelSecurityGroup"]["result"] = WIC_RES_SUCCESS
                    return kwargs
                except novaclient.exceptions.BadRequest:
                    kwargs["DelSecurityGroup"]["result"] = WIC_RES_FAILED
                    kwargs["DelSecurityGroup"]["note"] = 'groupName in use'
                    return kwargs
                except novaclient.exceptions.NotFound:
                    kwargs["DelSecurityGroup"]["result"] = WIC_RES_FAILED
                    kwargs["DelSecurityGroup"]["note"] = 'groupName not found'
                    return kwargs
                except:
                    kwargs["DelSecurityGroup"]["result"] = WIC_RES_FAILED
                    kwargs["DelSecurityGroup"]["note"] = 'error'
                    return kwargs
                    
        kwargs["DelSecurityGroup"]["result"] = WIC_RES_FAILED
        kwargs["DelSecurityGroup"]["note"] = 'groupName not found'
        return kwargs
    
    def StopHost(self, *args, **kwargs):
        ins_id = kwargs["StopHost"]["instanceId"]
        kwargs["StopHost"]["timestamp"] = wic_utils.get_timestamp()
        kwargs["StopHost"]["result"]  = self.instance_suspend(ins_id)
        return kwargs
    
    def DelHost(self, *args, **kwargs):
        kwargs["DelHost"]["note"] = default_note
        if not "instanceId" in kwargs["DelHost"].keys() or not kwargs["DelHost"]["instanceId"]:
            kwargs["DelHost"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["DelHost"]["instanceId"]
        res, hostip = self.netspeed_update(ins_id, 0)
        kwargs["DelHost"]["timestamp"] = wic_utils.get_timestamp()
        res, status = self.instance_show(ins_id)
        if res == WIC_RES_FAILED:
            kwargs["DelHost"]["result"] = res
            return kwargs
        if status == "PAUSED":
            res = self.instance_unpause(ins_id)
            kwargs["DelHost"]["result"] = self.waiting_ins_ready(ins_id)
            if kwargs["DelHost"]["result"] == WIC_RES_FAILED:
                kwargs["DelHost"]["note"] = "can't start host"
                return kwargs
        kwargs["DelHost"]["result"] = self.instance_delete(ins_id)
        return kwargs
    
    def CreateDisk(self, *args, **kwargs):
        if not "size" in kwargs["CreateDisk"].keys() or not kwargs["CreateDisk"]["size"]:
            kwargs["CreateDisk"]["result"] = WIC_RES_FAILED
            return kwargs
        size = kwargs["CreateDisk"]["size"]
        kwargs["CreateDisk"]["timestamp"] = wic_utils.get_timestamp()
        kwargs["CreateDisk"]["result"], kwargs["CreateDisk"]["volumeId"]  = self.volume_create(size)
        return kwargs
    
    def BindDisk(self, *args, **kwargs):
        if not "instanceId" in kwargs["BindDisk"].keys() or not kwargs["BindDisk"]["instanceId"] or \
        not "volumeId" in kwargs["BindDisk"].keys() or not kwargs["BindDisk"]["volumeId"]:
            kwargs["BindDisk"]["result"] = WIC_RES_FAILED
            return kwargs
        kwargs["BindDisk"]["note"] = default_note
        ins_id = kwargs["BindDisk"]["instanceId"]
        volume_id = kwargs["BindDisk"]["volumeId"]
        kwargs["BindDisk"]["timestamp"] = wic_utils.get_timestamp()
        if kwargs["BindDisk"]["type"] == 1 or kwargs["BindDisk"]["type"] == str(1):
            kwargs["BindDisk"]["result"] = self.auto_volume_attach(ins_id, volume_id)
            if kwargs["BindDisk"]["result"] == WIC_RES_FAILED:
                kwargs["BindDisk"]["note"] = "can not find volume id"
                return kwargs
            kwargs["BindDisk"]["result"] = self.waiting_volume_attached(volume_id)
        elif kwargs["BindDisk"]["type"] == 2 or kwargs["BindDisk"]["type"] == str(2):
            kwargs["BindDisk"]["result"] = self.volume_dettach(ins_id, volume_id)
            if kwargs["BindDisk"]["result"] == WIC_RES_FAILED:
                kwargs["BindDisk"]["note"] = "can not find volume id"
                return kwargs
            kwargs["BindDisk"]["result"] = self.waiting_volume_detached(volume_id)
            if kwargs["BindDisk"]["result"] == WIC_RES_FAILED:
                kwargs["BindDisk"]["note"] = "failed detahced"
                return kwargs
            wic_utils.delete_device_location(ins_id, volume_id)
            if disk_hotplug == False:
                res, status = self.instance_show(ins_id)
                print status
                if status == "PAUSED":
                    time.sleep(1)
                    kwargs["BindDisk"]["result"] = self.instance_unpause(ins_id)
                    kwargs["BindDisk"]["result"] = self.waiting_ins_ready(ins_id)
                    kwargs["BindDisk"]["result"] = self.instance_reboot(ins_id)
                    kwargs["BindDisk"]["result"] = self.waiting_ins_ready(ins_id)
                    kwargs["BindDisk"]["result"] = self.instance_pause(ins_id)
                    kwargs["BindDisk"]["result"] = self.waiting_ins_ready(ins_id)
                else:
                    time.sleep(1)
                    kwargs["BindDisk"]["result"] = self.instance_reboot(ins_id)
                    kwargs["BindDisk"]["result"] = self.waiting_ins_ready(ins_id)
        return kwargs
    
    def wic_volume_dettach(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"] or \
        not kwargs.has_key("volumeId") or not kwargs["volumeId"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        volume_id = kwargs["volumeId"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"] = self.volume_dettach(ins_id, volume_id)
        return kwargs
    
    def DelDisk(self, *args, **kwargs):
        kwargs["DelDisk"]["note"] = default_note
        if not "volumeId" in kwargs["DelDisk"].keys() or not kwargs["DelDisk"]["volumeId"]:
            kwargs["DelDisk"]["result"] = WIC_RES_FAILED
            kwargs["DelDisk"]["note"] = "no volumeId input"
            return kwargs
        volume_id = kwargs["DelDisk"]["volumeId"]
        res, status, ins_id = self.volume_show(volume_id)
        if res == WIC_RES_FAILED:
            kwargs["DelDisk"]["result"] = WIC_RES_FAILED
            kwargs["DelDisk"]["note"] = "can not find the volume"
            return kwargs
        if status == "available":
            kwargs["DelDisk"]["result"] = self.volume_delete(volume_id)
        elif status == "in-use":
            kwargs["DelDisk"]["result"] = self.volume_dettach(ins_id, volume_id)
            kwargs["DelDisk"]["result"] = self.waiting_volume_detached(volume_id)
            kwargs["DelDisk"]["result"] = self.volume_delete(volume_id)
            if disk_hotplug == False:
                kwargs["DelDisk"]["result"] = self.instance_reboot(ins_id)
        return kwargs
    
    def RestartHost(self, *args, **kwargs):
        kwargs["RestartHost"]["note"] = default_note
        if not "instanceId" in kwargs["RestartHost"].keys() or not kwargs["RestartHost"]["instanceId"]:
            kwargs["RestartHost"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["RestartHost"]["instanceId"]
        kwargs["RestartHost"]["result"] = self.instance_reboot(ins_id)
        return kwargs
    
    def ShutdownHost(self, **kwargs):
        kwargs["ShutdownHost"]["note"] = default_note
        if not kwargs["ShutdownHost"]["instanceId"]:
            kwargs["ShutdownHost"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["ShutdownHost"]["instanceId"]
        kwargs["ShutdownHost"]["result"] = self.instance_pause(ins_id)
        return kwargs
    
    def StartHost(self, **kwargs):
        kwargs["StartHost"]["note"] = default_note
        if not kwargs["StartHost"]["instanceId"]:
            kwargs["StartHost"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["StartHost"]["instanceId"]
        kwargs["StartHost"]["result"] = self.instance_unpause(ins_id)
        return kwargs
        
    def ApplyIp(self, *args, **kwargs):
        kwargs["ApplyIp"]["note"] = default_note
        kwargs["ApplyIp"]["timestamp"] = wic_utils.get_timestamp()
        if kwargs["ApplyIp"]["type"] == 1 or kwargs["ApplyIp"]["type"] == str(1):
            kwargs["ApplyIp"]["result"], kwargs["ApplyIp"]["ip"] = self.floating_ip_create()
        if kwargs["ApplyIp"]["type"] == 2 or kwargs["ApplyIp"]["type"] == str(2):
            kwargs["ApplyIp"] = self.floating_ip_delete(kwargs["ApplyIp"]["ip"])
        return kwargs
    
    def BindIp(self, *args, **kwargs):
        kwargs["BindIp"]["note"] = default_note
        if not "instanceId" in kwargs["BindIp"].keys() or not kwargs["BindIp"]["instanceId"] or \
        not "ip" in kwargs["BindIp"].keys() or not kwargs["BindIp"]["ip"]:
            kwargs["BindIp"]["result"] = WIC_RES_FAILED
            kwargs["BindIp"]["note"] = 'BindIp error, please check instanceId, ip'
            return kwargs
        ins_id = kwargs["BindIp"]["instanceId"]
        ipaddr = kwargs["BindIp"]["ip"]
        kwargs["BindIp"]["timestamp"] = wic_utils.get_timestamp()
        kwargs["BindIp"]["result"], kwargs["BindIp"]["note"] = self.floating_ip_add(ins_id, ipaddr)
        return kwargs
    
    def UnbindIp(self, *args, **kwargs):
        kwargs["UnbindIp"]["note"] = default_note
        ins_id = kwargs["UnbindIp"]["instanceId"]
        ipaddr = kwargs["UnbindIp"]["ip"]
        kwargs["UnbindIp"]["timestamp"] = wic_utils.get_timestamp()
        kwargs["UnbindIp"]["result"] = self.floating_ip_remove(ins_id, ipaddr)
        return kwargs
    
    def UpdateNetSpeed(self, *args, **kwargs):
        kwargs["UpdateNetSpeed"]["note"] = default_note
        if not kwargs["UpdateNetSpeed"]["instanceId"]: 
            kwargs["UpdateNetSpeed"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["UpdateNetSpeed"]["instanceId"]
        if not kwargs["UpdateNetSpeed"]["netSpeed"]: return WIC_RES_FAILED
        netspeed = kwargs["UpdateNetSpeed"]["netSpeed"]
        kwargs["UpdateNetSpeed"]["result"], hostip  = self.netspeed_update(ins_id, netspeed)
        return kwargs
    
    def CreateSnapshot(self, **kwargs):
        if not kwargs["CreateSnapshot"]["volumeId"]:
             kwargs["CreateSnapshot"]["result"] = WIC_RES_FAILED
             return kwargs
        volume_id = kwargs["CreateSnapshot"]["volumeId"]
        kwargs["CreateSnapshot"]["result"], kwargs["CreateSnapshot"]["snapshotId"] = \
        self.volume_snapshot_create(volume_id)
        return kwargs
    
    def DeleteSnapshot(self, **kwargs):
        if not kwargs["DeleteSnapshot"]["snapshotId"]:
            kwargs["DeleteSnapshot"]["result"] = WIC_RES_FAILED
            return kwargs
        snapshot_id = kwargs["DeleteSnapshot"]["snapshotId"]
        kwargs["DeleteSnapshot"]["result"] = self.volume_snapshot_delete(snapshot_id)
        return kwargs
    
    def CreateImage(self, **kwargs):
        if not kwargs["CreateImage"]["imageType"]: return WIC_RES_FAILED
        image_type = kwargs["CreateImage"]["imageType"]
        image_id = self.find_image(image_type)
        if not image_id: 
            kwargs["CreateImage"]["result"] = WIC_RES_FAILED
            kwargs["CreateImage"]["imageId"] = None
        else:
            kwargs["CreateImage"]["result"] = WIC_RES_SUCCESS
            kwargs["CreateImage"]["imageId"] = image_id
        return kwargs
        
    def DeleteImage(self, **kwargs):
        kwargs["DeleteImage"]["result"] = WIC_RES_FAILED
        return kwargs
        

if __name__ == '__main__':
    pass
