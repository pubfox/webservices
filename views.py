#coding=utf8
from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase
from spyne.model.primitive import AnyXml, AnyDict, String
from spyne.server.django import DjangoApplication
from spyne.util.xml import get_xml_as_object
from django.views.decorators.csrf import csrf_exempt
from .utils import clear_list, get_method
from .settings import *
from .etreeconv import root_dict_to_etree
from lxml import etree
import logging
logger = logging.getLogger('horizon')

#Install pyjnius steps:
#apt-get install build-essential openjdk-7-jdk cython python-dev
#python setup.py install
try:
    from jnius import autoclass as Java
    EncryptHandler = Java(ENCRYPT_CLASS_PATH)
except:
    pass

from .wic.wic_client import wic_client
c = wic_client()

def handle_request(params):
    method = get_method(params)
    method_name = METHOD_NAMES.get(method, method)
    if not hasattr(c, method):
        return (ID_FAIL, method_name+'暂未实现')
    try:
        _handle_request(params)
        return (ID_SUCCESS, '请求'+method_name+'成功')
    except:
        return (ID_FAIL, '请求'+method_name+'失败')

def _handle_request(params):
    pass

class WebService(ServiceBase):

    @srpc(String, _returns=String)
    def call(xml):
        #Decrypt request
        xml = EncryptHandler.get_decrypt_by_password(xml, ENCRYPT_PASSWORD)
        xml = AnyXml.from_string(xml)
        #Process params from request
        params = get_xml_as_object(xml, AnyDict)
        params = clear_list(params)
        #Handle request
        id, description = handle_request(params)
        res = root_dict_to_etree({'result': {'id': id, 'description': description}})
        res = etree.tostring(res)
        res = '<?xml version="1.0" encoding="UTF-8"?>' + res
        return res

    @srpc(AnyXml, _returns=AnyDict)
    def test(xml):
        params = get_xml_as_object(xml, AnyDict)
        params = clear_list(params)
        method = get_method(params)
        if not hasattr(c, method):
            raise Exception, 'Not implemented method: %s' % method
        return getattr(c, method)(**params)

soap_services = csrf_exempt(DjangoApplication(Application([WebService],
        'soap.services',
        in_protocol=Soap11(),
        out_protocol=Soap11(),
    )))
