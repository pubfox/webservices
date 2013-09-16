#coding=utf8
from wic_client_defines import *
import wic_utils
import time
from pprint import pprint as pp
import urllib2
from spyne.util.odict import odict
import re

class wic_client(object):
    def __init__(self):
        self.client = wic_utils.Client(osuser, ospassword, default_tenant, auth_uri, service_type='compute')
        self.volume_client = wic_utils.Client(osuser, ospassword, default_tenant, auth_uri, service_type='volume')
        self.keystone_client = wic_utils.KeyStoneClient(username=osuser, password=ospassword, tenant_name=default_tenant, auth_url=auth_uri)
    
    def _wait_instance_ready(self, instance_id, status='ACTIVE'):
        try_times = 0
        while try_times < default_try_times:
            instance = self.client.servers.get(instance_id)
            _status = instance.status
            print '%s:%s' % (instance.name, _status)
            if _status == status: return WIC_RES_SUCCESS
            try_times += 1
            time.sleep(default_sleep_time)
        raise Exception('instance can not be %s' % status)
    
    def _wait_volume_ready(self, volume_id, status='available'):
        try_times = 0
        while try_times < default_try_times:
            volume = self.volume_client.volumes.get(volume_id)
            _status = volume.status
            print '%s:%s' % (volume.display_name, _status)
            if _status == status: return WIC_RES_SUCCESS
            try_times += 1
            time.sleep(default_sleep_time)
        raise Exception('volume can not be %s' % status)
    
    def _netspeed_update(self, instance, netspeed):
        host = instance.__dict__.get('OS-EXT-SRV-ATTR:host')
        hostip = HOST_MAP.get(host, None)
        if not hostip:
            raise Exception('can not find instance hostip')
        uri = "http://" + str(hostip) + ":" + DEV_CTL_PORT + "/instance_device/netspeed/" + str(instance.id) + "/" + str(netspeed)
        req = urllib2.Request(uri)
        fd = urllib2.urlopen(req)
        ret = fd.read(3)
        if ret == "nok":
            raise Exception('can not set instance netspeed')
        return WIC_RES_SUCCESS, hostip
    
    def _make_active(self, instance):
        if instance.status == 'SUSPENDED':
            instance.resume()
        elif instance.status == 'STOPPED':
            instance.start()
        elif instance.status == 'PAUSED':
            instance.unpause() 
        elif instance.status in ['ACTIVE', 'SHUTOFF']:
            instance.reboot()
        else:
            raise Exception('Instance status wrong')
    
    def StartHost(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            self._make_active(instance)
            self._wait_instance_ready(instance.id)
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def StopHost(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            self._wait_instance_ready(instance.id)
            instance.pause()
            self._wait_instance_ready(instance.id, status='PAUSED')
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def RestartHost(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            self._wait_instance_ready(instance.id)
            instance.reboot('HARD')
            self._wait_instance_ready(instance.id)
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def ShutdownHost(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            self._wait_instance_ready(instance.id)
            instance.reboot('HARD')
            self._wait_instance_ready(instance.id)
            time.sleep(default_sleep_time * 10)
            instance.suspend()
            self._wait_instance_ready(instance.id, status='SUSPENDED')
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def DelHost(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            self._make_active(instance)
            self._wait_instance_ready(instance.id)
            
            volumes = self.volume_client.volumes.list()
            for volume in volumes:
                if volume.attachments:
                    for attachment in volume.attachments:
                        if attachment['server_id'] == instance.id:
                            self.client.volumes.delete_server_volume(attachment['server_id'], attachment['volume_id'])
                            self._wait_volume_ready(attachment['volume_id'])
                            time.sleep(default_sleep_time * DEFAULT_MULTI)
            
            ips = self.client.floating_ips.findall(instance_id=instance.id)
            for ip in ips:
                instance.remove_floating_ip(ip)
                time.sleep(default_sleep_time)
            self._wait_instance_ready(instance.id)
            instance.delete()
            time.sleep(default_sleep_time * 10)
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def CreateSnapshot(self, **kwargs):
        try:            
            volume = self.volume_client.volumes.get(kwargs['volumeId'])
            snapshot = self.volume_client.volume_snapshots.create(volume.id, force=True)
            
            kwargs['snapshotId'] = snapshot.id
            kwargs['startTime'] = wic_utils.get_timestamp()
            kwargs['status'] = snapshot.status
            kwargs['progress'] = ''
            kwargs['volSize'] = volume.size
            kwargs['isSystemSnap'] = ''
            kwargs['InstanceId'] = ''
            kwargs['ImageId'] = ''
            
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def RestoreSnapShot(self, **kwargs):
        try:            
            snapshot = self.volume_client.volume_snapshots.get(kwargs['snapshotId'])
            #todo: how to restore?
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def DeleteSnapshot(self, **kwargs):
        try:            
            snapshot = self.volume_client.volume_snapshots.get(kwargs['snapshotId'])
            snapshot.delete()
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def CreateSecurityGroup(self, **kwargs):
        try:
            groupName = kwargs.get('groupName')
            if not groupName:
                raise Exception('groupName can not be blank')
            groupName = groupName.strip()
            group = self.client.security_groups.create(groupName, default_sec_desc)
            self.client.security_group_rules.create(group.id, ip_protocol='tcp', from_port=3389, to_port=3389, cidr=None, group_id=None)
            self.client.security_group_rules.create(group.id, ip_protocol='tcp', from_port=22, to_port=22, cidr=None, group_id=None)
            self.client.security_group_rules.create(group.id, ip_protocol='tcp', from_port=1, to_port=65535, cidr=None, group_id=group.id)
            self.client.security_group_rules.create(group.id, ip_protocol='udp', from_port=1, to_port=65535, cidr=None, group_id=group.id)
            self.client.security_group_rules.create(group.id, ip_protocol='icmp', from_port=-1, to_port=255, cidr=None, group_id=group.id)
            del kwargs['groupSize']
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def DescribeSecurityGroup(self, **kwargs):
        try:
            group = self.client.security_groups.find(name=kwargs['groupName'])
            kwargs['groupList'] = {'groupName': group.name, 'groupSize': DEFAULT_NUMBER}
            del kwargs['groupName']
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except wic_utils.NotFound:
            kwargs['note'] = 'groupName not found'
            kwargs['result'] = WIC_RES_FAILED
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def DelSecurityGroup(self, **kwargs):
        try:
            group = self.client.security_groups.find(name=kwargs['groupName'])
            group.delete()
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except wic_utils.NotFound:
            kwargs['note'] = 'groupName not found'
            kwargs['result'] = WIC_RES_FAILED
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def ApplyIp(self, **kwargs):
        try:
            instance = self.client.servers.get(kwargs['instanceId'])
            type = int(kwargs['type'])
            if type == 1:
                ip = self.client.floating_ips.create()
                time.sleep(default_sleep_time)
                instance.add_floating_ip(ip)
                kwargs['ip'] = ip.ip
            elif type == 2:
                ip = self.client.floating_ips.find(ip=kwargs['ip'])
                if not ip.instance_id == instance.id:
                    raise Exception('ip is not binded with this instance')
                instance.remove_floating_ip(ip)
            else:
                raise Exception('type error')
            del kwargs['type']
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def BindIp(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            ip = self.client.floating_ips.find(ip=kwargs['ip'])
            if ip.instance_id:
                raise Exception('ip already loaded')
            instance.add_floating_ip(ip)
            time.sleep(default_sleep_time * DEFAULT_MULTI)
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def UnbindIp(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            ip = self.client.floating_ips.find(ip=kwargs['ip'])
            if not ip.instance_id == instance.id:
                raise Exception('ip is not binded with this instance')
            instance.remove_floating_ip(ip)
            time.sleep(default_sleep_time * DEFAULT_MULTI)
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def CreateImage(self, **kwargs):
        try:
            raise Exception('not implement')
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def DeleteImage(self, **kwargs):
        try:
            image = self.client.images.get(kwargs['imageId'])
            image.delete()
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def UpdateOs(self, **kwargs):
        try:
            instance = self.client.servers.get(kwargs['instanceId'])
            image = self.client.images.find(name=kwargs['os'])
            instance.rebuild(image, password=default_ins_pass)
            self._wait_instance_ready(instance.id)
            del kwargs['os']
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def EmpowerPort(self, **kwargs):
        try:
          parent_group = self.client.security_groups.find(name=kwargs['groupName'])
          parent_group_id = parent_group.id
          ipPermissions = kwargs['ipPermissions']
          if isinstance(ipPermissions, odict) or isinstance(ipPermissions, dict):
            ipPermissions = [ipPermissions]
          for ipPermission in ipPermissions:
            from_port = int(ipPermission['startPort'])
            to_port = int(ipPermission['endPort'])
            ip_protocol = ipPermission['ipProtocol']
            cidr = None
            group_id = None
            if 'ipRanges' in ipPermission.keys() and 'groups' in ipPermission.keys():
                raise Exception('ipRanges or groups, can not both')
            if 'ipRanges' in ipPermission.keys():
                cidr = ipPermission['ipRanges']['cidrIp']
            if 'groups' in ipPermission.keys():
                group = self.client.security_groups.find(name=ipPermission['groups']['gGroupName'])
                group_id = group.id
            type = int(kwargs['type'])
            if type in [1, 3]:
                self.client.security_group_rules.create(parent_group_id, ip_protocol=ip_protocol, from_port=from_port, to_port=to_port, cidr=cidr, group_id=group_id)
            elif type in [2, 4]:
                rule_id = None
                for rule in parent_group.rules:
                    if cidr and rule['from_port'] == from_port and rule['to_port'] == to_port and rule['ip_protocol'] == ip_protocol and rule['ip_range']['cidr'] == cidr:
                        rule_id = rule['id']
                        break
                    if group_id and rule['from_port'] == from_port and rule['to_port'] == to_port and rule['ip_protocol'] == ip_protocol and rule['group'].get('name', None) == group.name:
                        rule_id = rule['id']
                        break
                if not rule_id:
                    raise Exception('Rule not found')
                self.client.security_group_rules.delete(rule_id)
            else:
                raise Exception('type error')
          kwargs['note'] = default_note
          kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
          kwargs['note'] = 'This rule already exists in group' if e.message.startswith('This rule already exists in group') else e.message
          kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def CreateDisk(self, **kwargs):
        try:
            size = kwargs.get('size', None)
            if not size:
                raise Exception('size can not be blank')
            size = int(size.strip())
            if not size > 0:
                raise Exception('size should be >= 1')
            display_name = 'vol_%s' % kwargs.get('transactionId', None)
            volume = self.volume_client.volumes.create(size, display_name=display_name)
            self._wait_volume_ready(volume.id)
            if 'instanceId' in kwargs.keys():
                if kwargs['instanceId']:
                    instance = self.client.servers.get(kwargs['instanceId'])
                    self.client.volumes.create_server_volume(instance.id, volume.id, None)
                    self._wait_volume_ready(volume.id, status='in-use')
                    time.sleep(default_sleep_time * DEFAULT_MULTI)
                del kwargs['instanceId']
            volume = self.volume_client.volumes.get(volume.id)
            kwargs['volumeId'] = volume.id
            kwargs['snapshotId'] = ''
            kwargs['zone'] = ''
            kwargs['status'] = volume.status
            kwargs['volumeType'] = ''
            kwargs['createTime'] = wic_utils.get_timestamp()
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def BindDisk(self, **kwargs):
        try:            
            instance = self.client.servers.get(kwargs['instanceId'])
            _status = instance.status
            volume = self.volume_client.volumes.get(kwargs['volumeId'])
            type = int(kwargs['type'])
            if type == 1:
                if volume.attachments:
                    raise Exception('volume is already binded') 
                if not _status == 'ACTIVE':
                    self._make_active(instance)
                self._wait_instance_ready(instance.id)
                self.client.volumes.create_server_volume(instance.id, volume.id, None)
                self._wait_volume_ready(volume.id, status='in-use')
                kwargs["attachTime"] = wic_utils.get_timestamp()
            elif type == 2:
                if not volume.attachments:
                    raise Exception('volume is not binded') 
                if not _status == 'SUSPENDED':
                    raise Exception('instance should be shutdown')
                instance.resume()
                self._wait_instance_ready(instance.id)
                self.client.volumes.delete_server_volume(instance.id, volume.id)
                self._wait_volume_ready(volume.id)
                kwargs["attachTime"] = ''
            else:
                raise Exception('type error')
            time.sleep(default_sleep_time * DEFAULT_MULTI)
            try:
                if _status == 'SUSPENDED':
                    time.sleep(default_sleep_time * 10)
                    instance.suspend()
                    self._wait_instance_ready(instance.id, status='SUSPENDED')
            except:
                print 'BindDisk: instance %s can not suspend' % instance.id
            del kwargs['type']
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def DelDisk(self, **kwargs):
        time.sleep(default_sleep_time * 10)
        try:            
            volume = self.volume_client.volumes.get(kwargs['volumeId'])
            if volume.attachments:
                for attachment in volume.attachments:
                    instance = self.client.servers.get(attachment['server_id'])
                    _status = instance.status
                    self._make_active(instance)
                    self._wait_instance_ready(instance.id)
                    self.client.volumes.delete_server_volume(attachment['server_id'], attachment['volume_id'])
                    self._wait_volume_ready(attachment['volume_id'])
                    time.sleep(default_sleep_time * DEFAULT_MULTI)
                    instance.reboot()
                    self._wait_instance_ready(instance.id)
                    if _status == 'SUSPENDED':
                        time.sleep(default_sleep_time * 10)
                        instance.suspend()
                        self._wait_instance_ready(instance.id, status='SUSPENDED')
            volume.delete()
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def UpdateNetSpeed(self, **kwargs):
        try:
            instance = self.client.servers.get(kwargs['instanceId'])
            netspeed = kwargs.get('netSpeed', 0)
            netspeed = int(netspeed)
            if not netspeed >= 0:
                raise Exception('netSpeed should be >= 0')
            res, hostip = self._netspeed_update(instance, netspeed)
            #Save instance netspeed
            self.client.servers.set_meta(instance, {'netspeed':str(netspeed)})
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message or e.reason
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def CreateUser(self, **kwargs):
        try:
            name = kwargs.get('userName', None)
            email = kwargs.get('email', None)
            if not re.match('[^@]+@[^@]+\.[^@]+', email):
                raise Exception('Invalid email address')
            password = default_password
            tenant_id = self.keystone_client.tenants.find(name=default_tenant).id
            user = self.keystone_client.users.create(name, password, email, tenant_id=tenant_id, enabled=True)
            kwargs['note'] = default_note
            kwargs['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['note'] = e.message
            kwargs['result'] = WIC_RES_FAILED
        kwargs["timestamp"] = wic_utils.get_timestamp()
        return kwargs
    
    def Create(self, **kwargs):
        instance = None
        try:
            name = 'ins_%s' % kwargs['CreateHost']['transactionId']
            image = self.client.images.find(name=kwargs['CreateHost']['os'])
            security_groups = None if not kwargs['CreateHost']['groupName'] else \
                self.client.security_groups.find(name=kwargs['CreateHost']['groupName'])
            security_groups = None if security_groups is None else [security_groups.name]
            if 'hostSpecId' in kwargs['CreateHost'].keys() and kwargs['CreateHost']['hostSpecId']:
                flavor = self.client.flavors.get(kwargs['CreateHost']['hostSpecId'])
            else:
                vcpus = kwargs['CreateHost']['core']
                ram = kwargs['CreateHost']['memory']
                disk = kwargs['CreateHost']['disk']
                vcpus=int(vcpus)
                ram=int(float(ram) * 1024)
                disk=int(disk)
                flavors = self.client.flavors.findall(vcpus=vcpus, ram=ram, disk=disk)
                if flavors:
                    flavor = flavors[0]
                else:
                    flavor_name = 'flv_%s' % kwargs['CreateHost']['transactionId']
                    flavors_ids = [int(f.id) for f in self.client.flavors.list()]
                    flavor_id = max(flavors_ids) + 1
                    flavor = self.client.flavors.create(flavor_name, ram, vcpus, disk, flavor_id)
            instance = self.client.servers.create(name, image, flavor, security_groups=security_groups)
            self._wait_instance_ready(instance.id)
            
            kwargs['CreateHost']['instanceId'] = instance.id
            kwargs['CreateHost']['privateIp'] = ''
            kwargs['CreateHost']['osUserName'] = default_ins_name
            kwargs['CreateHost']['osPassword'] = default_ins_pass
            kwargs['CreateHost']['reservationId'] = ''
            kwargs['CreateHost']['vmName'] = ''
            kwargs['CreateHost']['imageId'] = image.id
            kwargs['CreateHost']['privateDnsName'] = instance.networks['net2'][0]
            kwargs['CreateHost']['dnsName'] = ''
            kwargs['CreateHost']['keyName'] = ''
            kwargs['CreateHost']['amiLaunchIndex'] = ''
            kwargs['CreateHost']['instanceType'] = ''
            kwargs['CreateHost']['placement'] = ''
            kwargs['CreateHost']['kernelId'] = ''
            kwargs['CreateHost']['ramvolumeId'] = ''
            kwargs['CreateHost']['isEnableHa'] = ''
            kwargs['CreateHost']['vpcId'] = ''
            kwargs['CreateHost']['mac'] = ''
            kwargs['CreateHost']['ipAddress'] = ''
            kwargs['CreateHost']['rateLimit'] = ''
            kwargs['CreateHost']['vmHostName'] = instance.name
            kwargs['CreateHost']['vncPort'] = ''
            kwargs['CreateHost']['snapshotId'] = ''
            kwargs['CreateHost']['sysVolumeId'] = ''
                       
            for k in ['core', 'memory', 'disk', 'os', 'hostSpecId', 'path']:
                if k in kwargs['CreateHost'].keys():
                    del kwargs['CreateHost'][k]
             
            kwargs['CreateHost']['note'] = default_note
            kwargs['CreateHost']['result'] = WIC_RES_SUCCESS
        except Exception, e:
            kwargs['CreateHost']['note'] = e.message
            kwargs['CreateHost']['result'] = WIC_RES_FAILED
        kwargs['CreateHost']["timestamp"] = wic_utils.get_timestamp()
        
        _need_to_do = False
        if instance and 'CreateDisk' in kwargs.keys() and 'disk' in kwargs['CreateDisk'].keys():
            disk = kwargs['CreateDisk']['disk']
            if disk:
                _need_to_do = True
        if _need_to_do:
          try:
            disk = int(disk)
            if not disk > 0:
                raise Exception('disk should be >= 1')
            display_name = 'vol_%s' % kwargs['CreateDisk'].get('transactionId', None)
            volume = self.volume_client.volumes.create(disk, display_name=display_name)
            self._wait_volume_ready(volume.id)
            self.client.volumes.create_server_volume(instance.id, volume.id, None)
            self._wait_volume_ready(volume.id, status='in-use')
            time.sleep(default_sleep_time * DEFAULT_MULTI)
            volume = self.volume_client.volumes.get(volume.id)
            kwargs['CreateDisk']['volumeId'] = volume.id
            kwargs['CreateDisk']['createTime'] = wic_utils.get_timestamp()
            kwargs['CreateDisk']['size'] = disk
            kwargs['CreateDisk']['status'] = volume.status
            kwargs['CreateDisk']['snapshotId'] = ''
            kwargs['CreateDisk']['zone'] = ''
            
            if 'disk' in kwargs['CreateDisk'].keys():
                del kwargs['CreateDisk']['disk']
            kwargs['CreateDisk']['note'] = default_note
          except Exception, e:
            kwargs['CreateDisk']['note'] = e.message
            instance.delete()
            instance = None
            kwargs['CreateHost']['note'] = e.message
            kwargs['CreateHost']['result'] = WIC_RES_FAILED
        
        _need_to_do = False
        if instance and 'CreateIp' in kwargs.keys() and 'netSpeed' in kwargs['CreateIp'].keys():
            netspeed = kwargs['CreateIp']['netSpeed']
            if netspeed:
                _need_to_do = True
        if _need_to_do:
          try:
            netspeed = int(netspeed)
            if not netspeed >= 0:
                raise Exception('netSpeed should be >= 0')
            res, hostip = self._netspeed_update(instance, netspeed)
            #Save instance netspeed
            self.client.servers.set_meta(instance, {'netspeed':str(netspeed)})
            kwargs['CreateIp']['note'] = default_note
          except Exception, e:
            kwargs['CreateIp']['note'] = e.message or e.reason
        time.sleep(default_sleep_time * 10)
        return kwargs

if __name__ == '__main__':
    c = wic_client()
    pass
