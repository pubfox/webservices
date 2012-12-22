import time
from wic_client_defines import *

def get_timestamp():
    return time.strftime(ISOTIMEFORMAT, time.localtime())