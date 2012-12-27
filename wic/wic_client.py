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
from urlparse import urlparse
from wic_client_defines import *
#from wic_floating import *


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
        self.host_len = wic_utils.get_hostmap(self.host_map)
    
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
    
    def instance_create(self):
        pass
    
    def secgroup_show(self):
        uri = self.apiurl + str('/os-security-groups')
        http = httplib2.Http()
        resp, content = http.request (uri, method = "GET", headers=self.headers)
        return json.loads(content)
    
    def secgroup_create(self, secgroup_name):
        uri = self.apiurl + str('/os-security-groups')
        body = {"security_group": {"name": secgroup_name, "description": default_sec_desc}}
        http = httplib2.Http()
        resp, content = http.request (uri, method = "POST", body = body, headers=self.headers)
        if resp.status == 200:
            data = json.loads(content)
            return WIC_RES_SUCCESS, data["security_group"]["id"]
        return WIC_RES_FAILED, None
    
    def secgroup_delete(self, secgroup_name):
        pass
        
    def instance_suspend(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"suspend" : None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def instance_delete(self, ins_id):
        uri = self.apiurl + "/servers/" + id
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200:
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
        if resp.status == 200:
            data = json.loads(content)
            volume_id = data["volume"]["id"]
            return WIC_RES_SUCCESS, volume_id
        return WIC_RES_FAILED, None
    
    def volume_attach(self, ins_id, volume_id, device = '/dev/vdx'):
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
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def volume_dettach(self, ins_id, volume_id):
        uri = self.apiurl + "/servers/" + ins_id + "/os-volume_attachments/" + str(volume_id)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def volume_delete(self, volume_id):
        uri = self.volumeurl + "/volumes/" + str(id)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def instance_reboot(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"reboot": {"type": "SOFT"}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def instance_pause(self, ins_id):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"pause" : None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def floating_ip_create(self):
        uri = self.apiurl + '/os-floating-ips'
        body = {"pool": None}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS, content["floating_ip"]["ip"]
        return WIC_RES_FAILED, None        
    
    def floating_ip_add(self, ins_id, ipaddr):
        uri = self.apiurl + "/servers/" + ins_id + "/action"
        body = {"addFloatingIp": {"address": ip}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    
    def floating_ip_delete(self, ins_id, ipaddr):
        pass
    
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
        req = urllib2.Request(uri)
        fd = urllib2.urlopen(req)
        ret = fd.read(3)
        if ret == "nok":
            return WIC_RES_FAILED, hostip  
        return WIC_RES_SUCCESS, hostip
    
    def volume_snapshot_create(self, volume_id):
        uri = self.apiurl + "/snapshots"
        body = {"snapshot": {"display_name": null, "force": false, "display_description": null, "volume_id": volume_id}}
        body = json.dumps(body)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "POST", body = body, headers = self.headers)
        if resp.status == 200:
            data = json.loads(content)
            return WIC_RES_SUCCESS, content["snapshot"]["id"]
        return WIC_RES_FAILED, None
    
    def volume_snapshot_delete(self, snapshot_id):
        uri = self.apiurl + "/snapshots/" + str(snapshot_id)
        http = httplib2.Http()
        resp, content = http.request(uri, method = "DELETE", headers = self.headers)
        if resp.status == 200:
            return WIC_RES_SUCCESS
        return WIC_RES_FAILED
        

class wic_client(Base):
    def __init__(self, tenant = default_tenant):
        super(wic_client, self).__init__()
    
    def wic_add_user(self, *args, **kwargs):
        if not kwargs["CreateUser"]["userName"]: return WIC_RES_FAILED
        username = kwargs["CreateUser"]["userName"]
        if not kwargs.has_key("requestId") or not kwargs["requestId"]:
            kwargs["requestId"] = default_requestId
        if not kwargs["CreateUser"].has_key("password"):
            kwargs["CreateUser"]["password"] = default_password
        password = kwargs["CreateUser"]["password"]
        if not kwargs.has_key("email"):
            kwargs["CreateUser"]["email"] = default_email
        email = kwargs["CreateUser"]["email"]
        if not kwargs["CreateUser"].has_key("tenantId"):
            kwargs["CreateUser"]["tenantId"] = self.tenant_id
        tenantId = kwargs["CreateUser"]["tenantId"]
        kwargs["CreateUser"]["timestamp"] = wic_utils.get_timestamp()
        status, userId = self.add_user(username, password, email, tenantId)
        kwargs["CreateUser"]["userId"] = userId
        return kwargs
    
    def CreateSecurityGroup(self, **kwargs):
        if not kwargs["CreateSecurityGroup"]["groupName"]:
            kwargs["CreateSecurityGroup"]["result"] = WIC_RES_FAILED
            return kwargs
        secgroup_name = kwargs["CreateSecurityGroup"]["groupName"]
        kwargs["CreateSecurityGroup"]["result"], id = self.secgroup_create(secgroup_name)
        return kwargs
        
    def DescribeSecurityGroup(self, *args, **kwargs):
        kwargs["result"] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        secgroup_name = kwargs["groupName"]
        all_secgroups = self.secgroup_show()
        for secgroup in all_secgroups['security_groups']:
            if secgroup['name'] == secgroup_name:
                kwargs["result"] = WIC_RES_SUCCESS
        return kwargs
    
    def DelSecurityGroup(self, **kwargs):
        pass
    
    def StopHost(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"]  = self.instance_suspend(ins_id)
        return kwargs
    
    def DelHost(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"] = self.instance_delete(ins_id)
        return kwargs
    
    def CreateDisk(self, *args, **kwargs):
        if not kwargs.has_key("disk") or not kwargs["disk"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        size = kwargs["disk"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"], kwargs["volumeId"]  = self.volume_create(size)
        return kwargs
    
    def BindDisk(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"] or \
        not kwargs.has_key("volumeId") or not kwargs["volumeId"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        volume_id = kwargs["volumeId"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"] = self.volume_attach(ins_id, volume_id)
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
        if not kwargs["DelDisk"].has_key("volumeId") or not kwargs["DelDisk"]["volumeId"]:
            kwargs["DelDisk"]["result"] = WIC_RES_FAILED
        volume_id = kwargs["DelDisk"]["volumeId"]
        kwargs["DelDisk"]["result"] = self.volume_delete(volume_id)
        return kwargs
    
    def RestartHost(self, *args, **kwargs):
        if not kwargs["RestartHost"].has_key("instanceId") or not kwargs["RestartHost"]["instaceId"]:
            kwargs["RestartHost"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["RestartHost"]["instaceId"]
        kwargs["RestartHost"]["result"] = self.instance_reboot(ins_id)
        return kwargs
    
    def ShutdownHost(self, **kwargs):
        if not kwargs["ShutdownHos"]["instanceId"]:
            kwargs["ShutdownHos"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["ShutdownHos"]["instanceId"]
        kwargs["ShutdownHos"]["result"] = self.instance_pause(ins_id)
        return kwargs
        
    def ApplyIp(self, *args, **kwargs):
        kwargs["CreateIp"]["result"], kwargs["CreateIp"]["ip"] = self.floating_ip_create()
        return kwargs
    
    def BindIp(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"] or \
        not kwargs.has_key("ip") or not kwargs["ip"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        ipaddr = kwargs["ip"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"] = self.floating_ip_add(ins_id, ipaddr)
        return kwargs
    
    def UnbindIp(self, *args, **kwargs):
        return kwargs
    
    def UpdateNetSpeed(self, *args, **kwargs):
        if not kwargs["UpdateNetSpeed"]["instanceId"]: 
            kwargs["UpdateNetSpeed"]["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["UpdateNetSpeed"]["instanceId"]
        if not kwargs.has_key("requestId") or not kwargs["requestId"]:
            kwargs["requestId"] = default_requestId
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
    c = wic_client()
    #result = c.wic_secgroup_show(groupName = "default")
    params = {'requestId':"requestId"}
    params['UpdateNetSpeed'] = {
        'instanceId':'93707c4e-f547-4b13-9358-c18d8ff08555',
        'netSpeed': 10,
        'timestamp': "timestamp",
        }
    #res = c.wic_update_netspeed(**params)
    res = c.find_image("win2008")
    print res
    #result = c.wic_add_user(userName = "test", password = "123456")
    #result, volume_id = c.wic_volume_create(5)
    #result = c.wic_volume_attach("93707c4e-f547-4b13-9358-c18d8ff08555", 4)