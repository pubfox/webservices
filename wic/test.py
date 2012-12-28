#!/usr/bin/python

import wic
from wic.wic_client import wic_client

def secgroup_show():
    c = wic_client()
    res = c.wic_secgroup_show(groupName = "default")
    
def add_user(**params):
    c = wic_client()
    res = c.AddUser(**params)
    
def suspend_instance(**params):
    c = wic_client()
    res = c.StopHost(**params)