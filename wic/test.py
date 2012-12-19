#!/usr/bin/python

import wic
from wic.wic_client import wic_client

c = wic_client()
res = c.wic_secgroup_show("default")

print res