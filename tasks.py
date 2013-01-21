from .etreeconv import root_dict_to_etree
from lxml import etree
from .settings import *
from .wic.wic_client import wic_client
#c = wic_client()

#Install django-celery steps:
#pip install celery==2.4.7
#pip install django-celery==2.4.1
try:
    from celery.task import task
except:
    pass

try:
    from jnius import autoclass as Java
    EncryptHandler = Java(ENCRYPT_CLASS_PATH)
except:
    pass

@task
def _handle_request(method, params):
    #res = getattr(c, method)(**params)
    res = params
    res = root_dict_to_etree({'response': res})
    res = etree.tostring(res)
    res = '<?xml version="1.0" encoding="UTF-8"?>' + res
    print res
    res = EncryptHandler.get_encrypt_by_password(res, ENCRYPT_PASSWORD)
    #TODO: Send msg to xixin soap server
    _send_back_result.delay(res)

@task
def _send_back_result(result):
    print 'send: ' + result
