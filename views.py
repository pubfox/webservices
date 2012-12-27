from spyne.application import Application
from spyne.decorator import srpc
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase
from spyne.model.primitive import AnyDict, AnyXml
from spyne.server.django import DjangoApplication
from spyne.util.xml import get_xml_as_object
from django.views.decorators.csrf import csrf_exempt
from .utils import clear_list

from .wic.wic_client import wic_client
c = wic_client()

class WebService(ServiceBase):

    @srpc(AnyXml, _returns=AnyDict)
    def CreateUser(xml):
        params = clear_list(get_xml_as_object(xml, AnyDict))
        return c.wic_add_user(**params)

soap_services = csrf_exempt(DjangoApplication(Application([WebService],
        'soap.services',
        in_protocol=Soap11(),
        out_protocol=Soap11(),
    )))
