#coding=utf8
ENCRYPT_PASSWORD = 'qweeee'

METHOD_NAMES = {
'Create':'创建虚机',
'StopHost':'挂起虚机',
'DelHost':'删除虚机',
'CreateDisk':'创建磁盘',
'BindDisk':'绑定/解绑磁盘',
'DelDisk':'删除磁盘',
'RestartHost':'重启虚机',
'ShutdownHost':'关闭虚机',
'CreateSecurityGroup':'创建安全组',
'DescribeSecurityGroup':'查询安全组',
'DelSecurityGroup':'删除安全组',
'UpdateNetSpeed':'扩展带宽',
'UnbindIp':'解绑IP',
'BindIp':'绑定IP',
'ApplyIp':'申请/删除IP',
'UpdateOs':'变更操作系统',
'CreateSnapshot':'创建快照',
'DeleteSnapshot':'删除快照',
'RestoreSnapShot':'恢复快照',
'CreateImage':'创建镜像',
'DeleteImage':'删除镜像',
'StartHost':'开启虚机',
}

CALL_BACK_WSDL = 'http://222.211.85.14:8120/intf/service/HuaweiIaasService?wsdl'
#CALL_BACK_WSDL = 'http://www.189yun.cc:8120/intf/service/HuaweiIaasService?wsdl'
ID_SUCCESS = 0
ID_FAIL = 1
