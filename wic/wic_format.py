from wic_client_defines import *

def make_default_create_response(kwargs):
    kwargs["Create"]["CreateHost"]["result"] = WIC_RES_FAILED
    kwargs["Create"]["CreateHost"]["instanceId"] = None
    kwargs["Create"]["CreateHost"]["imageId"] = None
    kwargs["Create"]["CreateHost"]["privateIp"] = None
    kwargs["Create"]["CreateHost"]["osUserName"] = default_ins_name
    kwargs["Create"]["CreateHost"]["osPassword"] = default_ins_pass
    kwargs["Create"]["CreateHost"]["reservationId"] = default_reservationId
    kwargs["Create"]["CreateHost"]["vmName"] = default_vmname
    kwargs["Create"]["CreateHost"]["privateDnsName"] = default_privateDnsName
    kwargs["Create"]["CreateHost"]["dnsName"] = default_dnsName
    kwargs["Create"]["CreateHost"]["keyName"] = default_keypair
    kwargs["Create"]["CreateHost"]["amiLaunchIndex"] = None
    kwargs["Create"]["CreateHost"]["instanceType"] = None
    kwargs["Create"]["CreateHost"]["placement"] = None
    kwargs["Create"]["CreateHost"]["kernelId"] = None
    kwargs["Create"]["CreateHost"]["ramvolumeId"] = 0
    kwargs["Create"]["CreateHost"]["isEnableHa"] = False
    kwargs["Create"]["CreateHost"]["vpcId"] = 0
    kwargs["Create"]["CreateHost"]["mac"] = default_mac
    kwargs["Create"]["CreateHost"]["ipAddress"] = None
    kwargs["Create"]["CreateHost"]["rateLimit"] = None
    kwargs["Create"]["CreateHost"]["vmHostName"] = "ins_" + str(kwargs["requestId"])
    kwargs["Create"]["CreateHost"]["vncPort"] = 0
    kwargs["Create"]["CreateHost"]["snapshotId"] = 0
    kwargs["Create"]["CreateHost"]["sysVolumeId"] = 0
    kwargs["Create"]["CreateHost"]["note"] = default_note
    
    kwargs["Create"]["CreateDisk"]["note"] = None
    kwargs["Create"]["CreateDisk"]["volumeId"] = None
    kwargs["Create"]["CreateDisk"]["zone"] = None
    
    return kwargs