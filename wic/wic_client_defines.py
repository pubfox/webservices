#uri, userinfo..
token_uri          = "http://172.18.200.130:5000/v2.0/tokens"
osuser             = "admin"
ospassword         = "87827270"
default_tenant     = "demo"
default_flavor     = "m1.tiny"
default_images     = [ "linux_tty" ] 
instance_prefix    = "Chuandge_"
ins_list           = []
control_node       = ["show-01"]

#Magic
WIC_RES_SUCCESS    = 1
WIC_RES_FAILED     = 5

#ipmi config
IPMI_USER          = 'root'
IPMI_PASS          = '87827270'

#debug
DEBUG_MODE         = 0