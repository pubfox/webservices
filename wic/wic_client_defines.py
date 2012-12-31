#uri, userinfo..
token_uri          = "http://172.18.200.130:5000/v2.0/tokens"
key_uri            = "http://172.18.200.130:35357/v2.0"
osuser             = "admin"
ospassword         = "87827270"
default_tenant     = "demo"
default_email      = "changxu.liu@guoteng.com.cn"
default_requestId  = "abcdefgh00000000"
default_flavor     = "m1.tiny"
default_images     = [ "linux_tty" ] 
default_password   = "123456"
default_sec_desc   = "secgroup description"
default_keypair    = "key"
default_max_count  = 1
default_min_count  = 1

default_ins_name   = 'admin'
default_ins_pass   = 'admin'
default_reservationId = '123456'
default_vmname     = 'vmname'
default_privateDnsName = '192.168.133.1'
default_dnsName    = '8.8.8.8'
default_mac        = 'aa:bb:cc:dd:ee'

default_try_times  = 200
default_sleep_time = 5

instance_prefix    = "Chuandge_"
ins_list           = []
control_node       = ["show-01"]

#Magic
WIC_RES_SUCCESS    = 1
WIC_RES_FAILED     = 5

#port
DEV_CTL_PORT       = '8001'

#ipmi config
IPMI_USER          = 'root'
IPMI_PASS          = '87827270'

#debug
DEBUG_MODE         = 0

#format
ISOTIMEFORMAT      = '%Y-%m-%d %X'