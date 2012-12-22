#!/usr/bin/python

import wic
from wic.wic_client import wic_client

def secgroup_show():
    c = wic_client()
    res = c.wic_secgroup_show(groupName = "default")
    
def add_user():
    c = wic_client()
    res, user_id = c.wic_add_user(userName = 'username', password = 'password')
    
def suspend_instance():
    c = wic_client()
    res = c.wic_instance_suspend(instanceId = 'instanceId')
    
def delete_instance():
    c = wic_client()
    res = c.wic_instance_delete(instanceId = 'instanceId')
    
def create_volume():
    c = wic_client()
    res = c.wic_volume_create(disk = 5)

def attach_volume():
    c = wic_client()
    res = c.wic_volume_attach(instanceId = 'xxxxxxxxxxxx', volumeId = '5')
    
def dettach_volume():
    c = wic_client()
    res = c.wic_volume_dettach(instanceId = 'xxxxxxxxxx', volumeId = '5')