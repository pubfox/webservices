#!/usr/bin/python

import httplib2
import json
import sys
import time
import subprocess
import re
import os
import wic_utils
from urlparse import urlparse
from wic_client_defines import *


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
        self.headers =  {
                                    'X-Auth-Project-Id' : tenant,
                                    'User-Agent' : 'python-novaclient',
                                    'Content-Type' : 'application/json',
                                    'Accept' : 'application/json',
                                    'X-Auth-Token' : self.apitoken
                         }
        self.key_uri = key_uri
    
    def add_user(self, *args, **kwargs):
        uri = self.key_uri + "/users"
        self.key_headers = {'User-Agent': 'python-keystoneclient', 
                            'Content-Type': 'application/json', 
                            'X-Auth-Token': 'ADMIN'}
        
        body = {
                "user": 
                    {
                     "email": kwargs["email"], 
                     "password": kwargs["password"], 
                     "enabled": True, 
                     "name": kwargs["userName"], 
                     "tenantId": kwargs["tenantId"]
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


class wic_client(Base):
    def __init__(self, tenant = default_tenant):
        super(wic_client, self).__init__()
    
    def wic_add_user(self, *args, **kwargs):
        if not kwargs["userName"]: return WIC_RES_FAILED
        if not kwargs.has_key("requestId") or not kwargs["requestId"]:
            kwargs["requestId"] = default_requestId
        if not kwargs.has_key("password"):
            kwargs["password"] = default_password
        if not kwargs.has_key("email"):
            kwargs["email"] = default_email
        if not kwargs.has_key("tenantId"):
            kwargs["tenantId"] = None
        kwargs["timestamp"] = wic_utils.get_timestamp()
        status, userId = self.add_user(*args, **kwargs)
        kwargs["userId"] = userId
        return kwargs
        
    def wic_secgroup_show(self, *args, **kwargs):
        kwargs["result"] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        secgroup_name = kwargs["groupName"]
        all_secgroups = self.secgroup_show()
        for secgroup in all_secgroups['security_groups']:
            if secgroup['name'] == secgroup_name:
                kwargs["result"] = WIC_RES_SUCCESS
        return kwargs
    
    def wic_instance_suspend(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"]  = self.instance_suspend(ins_id)
        return kwargs
    
    def wic_instance_delete(self, *args, **kwargs):
        if not kwargs.has_key("instanceId") or not kwargs["instanceId"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        ins_id = kwargs["instanceId"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"] = self.instance_delete(ins_id)
        return kwargs
    
    def wic_volume_create(self, *args, **kwargs):
        if not kwargs.has_key("disk") or not kwargs["disk"]:
            kwargs["result"] = WIC_RES_FAILED
            return kwargs
        size = kwargs["disk"]
        kwargs["timestamp"] = wic_utils.get_timestamp()
        kwargs["result"], kwargs["volumeId"]  = self.volume_create(size)
        return kwargs
    
    def wic_volume_attach(self, *args, **kwargs):
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
    

if __name__ == '__main__':
    c = wic_client()
    result = c.wic_secgroup_show(groupName = "default")
    #result = c.wic_add_user(userName = "test", password = "123456")
    #result, volume_id = c.wic_volume_create(5)
    #result = c.wic_volume_attach("93707c4e-f547-4b13-9358-c18d8ff08555", 4)
    
    print result