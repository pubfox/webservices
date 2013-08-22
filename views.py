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
from .wic.wic_client_v2 import wic_client
from .tasks import _handle_request
import subprocess

def handle_request(params):
    method = get_method(params)
    if not method:
        return (ID_FAIL, '请求命令错误')
    method_name = METHOD_NAMES.get(method, method)
    if not hasattr(wic_client, method):
        return (ID_FAIL, method_name+'暂未实现')
    try:
        _handle_request.delay(method, params)
        return (ID_SUCCESS, '请求'+method_name+'成功')
    except:
        return (ID_FAIL, '请求'+method_name+'失败')

class WebService(ServiceBase):

    @srpc(String, _returns=String)
    def call(xml):
        #Decrypt request
        xml = subprocess.check_output(['java', '-jar', 'webservices/java/Encryptor.jar', '-decrypt', xml, ENCRYPT_PASSWORD]).strip()
        print xml
        xml = AnyXml.from_string(xml)
        #Process params from request
        params = get_xml_as_object(xml, AnyDict)
        params = clear_list(params)
        #Handle request
        id, description = handle_request(params)
        res = '''<?xml version="1.0" encoding="UTF-8"?>
                 <result>
                   <id>%s</id>
                   <description>%s</description>
                 </result>''' % (id, description, )
        return res.decode('utf8')

    @srpc(AnyXml, _returns=AnyDict)
    def test(xml):
        params = get_xml_as_object(xml, AnyDict)
        params = clear_list(params)
        method = get_method(params)
        c = wic_client()
        if not hasattr(c, method):
            raise Exception, 'Not implemented method: %s' % method
        kwargs = params[method]
        kwargs = getattr(c, method)(**kwargs)
        params[method] = kwargs
        return params

soap_services = csrf_exempt(DjangoApplication(Application([WebService],
        'soap.services',
        in_protocol=Soap11(),
        out_protocol=Soap11(),
    )))
