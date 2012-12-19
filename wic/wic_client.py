#!/usr/bin/python

import httplib2
import json
import sys
import time
import subprocess
import re
import os
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
    
    def instance_create(self):
        pass
    
    def secgroup_show(self):
        uri = self.apiurl + str('/os-security-groups')
        http = httplib2.Http()
        resp, body = http.request (uri, method = "GET", headers=self.headers)
        return json.loads(body)


class wic_client(Base):
    def __init__(self, tenant = default_tenant):
        super(wic_client, self).__init__()
        
    def wic_add_user(self, *args):
        pass
        
    def wic_secgroup_show(self, secgroup_name):
        all_secgroups = self.secgroup_show()
        for secgroup in all_secgroups['security_groups']:
            if secgroup['name'] == secgroup_name:
                return WIC_RES_SUCCESS
        return WIC_RES_FAILED
    

if __name__ == '__main__':
    c = wic_client()
    result = c.wic_secgroup_show("default")
    print result
    