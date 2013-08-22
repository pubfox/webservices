#!/usr/bin/python

import ast
import errno
import gettext
import json
import math
import netaddr
import optparse
import os
import StringIO
import sys

# If ../nova/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'nova', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

gettext.install('nova', unicode=1)

from nova.compat import flagfile
from nova import context
from nova import crypto
from nova import db
from nova import exception
from nova import flags
from nova import log as logging
from nova import quota
from nova import rpc
from nova import utils
from nova import version
from nova.api.ec2 import ec2utils
from nova.auth import manager
from nova.compute import instance_types
from nova.db import migration
from nova.volume import volume_types

FLAGS = flags.FLAGS
flags.DECLARE('flat_network_bridge', 'nova.network.manager')
flags.DECLARE('num_networks', 'nova.network.manager')
flags.DECLARE('multi_host', 'nova.network.manager')
flags.DECLARE('network_size', 'nova.network.manager')
flags.DECLARE('vlan_start', 'nova.network.manager')
flags.DECLARE('vpn_start', 'nova.network.manager')
flags.DECLARE('default_floating_pool', 'nova.network.manager')
flags.DECLARE('public_interface', 'nova.network.linux_net')

# Decorators for actions
def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('options', []).insert(0, (args, kwargs))
        return func
    return _decorator

flagfile = utils.default_flagfile('/etc/nova/nova.conf')

if flagfile and not os.access(flagfile, os.R_OK):
    st = os.stat(flagfile)
    print "Could not read %s. Re-running with sudo" % flagfile
    try:
        os.execvp('sudo', ['sudo', '-u', '#%s' % st.st_uid] + sys.argv)
    except Exception:
        print 'sudo failed, continuing as if nothing happened'
try:
    argv = FLAGS(sys.argv)
    logging.setup()
except IOError, e:
    if e.errno == errno.EACCES:
        print _('Please re-run nova-manage as root.')
        sys.exit(2)
    raise

class FloatingIpCommands(object):
    """Class for managing floating ip."""

    @staticmethod
    def address_to_hosts(addresses):
        """
        Iterate over hosts within a address range.

        If an explicit range specifier is missing, the parameter is
        interpreted as a specific individual address.
        """
        try:
            return [netaddr.IPAddress(addresses)]
        except ValueError:
            return netaddr.IPNetwork(addresses).iter_hosts()

    @args('--ip_range', dest="ip_range", metavar='<range>', help='IP range')
    @args('--pool', dest="pool", metavar='<pool>', help='Optional pool')
    @args('--interface', dest="interface", metavar='<interface>',
          help='Optional interface')
    def create(self, ip_range, pool=None, interface=None):
        """Creates floating ips for zone by range"""
        admin_context = context.get_admin_context()
        if not pool:
            pool = FLAGS.default_floating_pool
        if not interface:
            interface = FLAGS.public_interface
        for address in self.address_to_hosts(ip_range):
            db.floating_ip_create(admin_context,
                                  {'address': str(address),
                                   'pool': pool,
                                   'interface': interface})

    @args('--ip_range', dest="ip_range", metavar='<range>', help='IP range')
    def delete(self, ip_range):
        """Deletes floating ips by range"""
        for address in self.address_to_hosts(ip_range):
            db.floating_ip_destroy(context.get_admin_context(),
                                   str(address))

    @args('--host', dest="host", metavar='<host>', help='Host')
    def list(self, host=None):
        """Lists all floating ips (optionally by host)
        Note: if host is given, only active floating IPs are returned"""
        ctxt = context.get_admin_context()
        try:
            if host is None:
                floating_ips = db.floating_ip_get_all(ctxt)
            else:
                floating_ips = db.floating_ip_get_all_by_host(ctxt, host)
        except exception.NoFloatingIpsDefined:
            print _("No floating IP addresses have been defined.")
            return
        for floating_ip in floating_ips:
            instance_id = None
            if floating_ip['fixed_ip_id']:
                fixed_ip = db.fixed_ip_get(ctxt, floating_ip['fixed_ip_id'])
                try:
                    instance = db.instance_get(ctxt, fixed_ip['instance_id'])
                    instance_id = instance.get('uuid', "none")
                except exception.InstanceNotFound:
                    msg = _('Missing instance %s')
                    instance_id = msg % fixed_ip['instance_id']

            print "%s\t%s\t%s\t%s\t%s" % (floating_ip['project_id'],
                                          floating_ip['address'],
                                          instance_id,
                                          floating_ip['pool'],
                                          floating_ip['interface'])
            
if __name__ == '__main__':    
    ip = FloatingIpCommands()
    ip.create('172.18.200.20')
