#!/usr/bin/python

import wic
from wic.wic_client import wic_client

def secgroup_show(name):
    c = wic_client()
    res = c.wic_secgroup_show("default")
    
def add_user(username, password):
    c = wic_client()
    res, user_id = c.wic_add_user(username = username, password = password)
    
def suspend_instance(ins_id):
    c = wic_client()
    res = c.wic_instance_suspend(ins_id)
    
def delete_instance(ins_id):
    c = wic_client()
    res = c.wic_instance_delete(ins_id)