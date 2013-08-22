#uri, userinfo..
DEBUG = True
ip                 = '125.64.8.251'
token_uri          = "http://" + ip + ":5000/v2.0/tokens"
key_uri            = "http://" + ip +":35357/v2.0"
auth_uri = "http://" + ip + ":5000/v2.0"
osuser             = "admin"
ospassword         = "87827270"
default_tenant     = "demo"
default_email      = "changxu.liu@guoteng.com.cn"
default_requestId  = "abcdefgh00000000"
default_flavor     = "m1.tiny"
default_images     = [ "linux_tty" ] 
default_password   = "123456"
default_sec = 'default'
default_sec_desc   = "secgroup description"
default_keypair    = "key01"
default_max_count  = 1
default_min_count  = 1

default_note       = "success"
default_ins_name   = 'root'
default_ins_pass   = 'yjs68@GT'
default_reservationId = '123456'
default_vmname     = 'cloudhost'
default_privateDnsName = ''
default_dnsName    = '8.8.8.8'
default_mac        = ''

default_try_times  = 20
default_sleep_time = 10
DEFAULT_MULTI = 2
DEFAULT_NUMBER = 8
DEFAULT_DEVICE = '/dev/vd'

instance_prefix    = "Chuandge_"
ins_list           = []
control_node       = ["show-01"]

disk_hotplug       = False


attach_file        = "/tmp/wic/attach_file"

#Magic
WIC_RES_SUCCESS    = 0
WIC_RES_FAILED     = 1

#port
DEV_CTL_PORT       = '8001'

#ipmi config
IPMI_USER          = 'root'
IPMI_PASS          = '87827270'

#debug
DEBUG_MODE         = 0

#format
ISOTIMEFORMAT      = '%Y-%m-%d %X'

HOST_MAP = {
'ctrl-01':'172.18.56.20',
'ctrl-02':'172.18.56.21',
'comp-22':'172.18.56.22',
'comp-23':'172.18.56.23',
'comp-24':'172.18.56.24',
'comp-25':'172.18.56.25',
'comp-26':'172.18.56.26',
'comp-27':'172.18.56.27',
'comp-28':'172.18.56.28',
}
