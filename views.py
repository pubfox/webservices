from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase
from spyne.model.primitive import AnyXml, AnyDict, String
from spyne.server.django import DjangoApplication
from spyne.util.xml import get_xml_as_object
from django.views.decorators.csrf import csrf_exempt
from .utils import clear_list, get_method
from .settings import ENCRYPT_PASSWORD, ENCRYPT_CLASS_PATH
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

class WebService(ServiceBase):

    @srpc(String, _returns=String)
    def call(xml):
        #Decrypt request
        xml = EncryptHandler.get_decrypt_by_password(xml, ENCRYPT_PASSWORD)
        xml = AnyXml.from_string(xml)
        #process
        params = get_xml_as_object(xml, AnyDict)
        params = clear_list(params)
        method = get_method(params)
        if not hasattr(c, method):
            raise Exception, 'Not implemented method: %s' % method
        res = getattr(c, method)(**params)
        #Encrypt response
        res = root_dict_to_etree({'response': res})
        res = etree.tostring(res, encoding='utf8')
        res = '<?xml version="1.0" encoding="UTF-8"?>' + res
        return EncryptHandler.get_encrypt_by_password(res, ENCRYPT_PASSWORD)

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
