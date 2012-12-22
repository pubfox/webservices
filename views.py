from spyne.application import Application
from spyne.decorator import srpc, rpc
from spyne.protocol.soap import Soap11
from spyne.protocol.http import HttpRpc
from spyne.service import ServiceBase
from spyne.model.complex import Array, Iterable, ComplexModel
from spyne.model.primitive import Integer, Float, Unicode, Boolean, String, AnyDict
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt

from .wic.wic_client import wic_client
c = wic_client()

class WebService(ServiceBase):
    @srpc(String, Unicode, String, String, String, _returns=AnyDict)
    def CreateUser(requestId, userName, phoneNumber, email, timestamp):
        params = {'requestId':requestId}
        params['CreateUser'] = {
		'userName':userName,
		'phoneNumber':phoneNumber,
		'email':email,
		'timestamp':timestamp,
		}
        res = c.wic_add_user(**params)
        return res

soap_services = csrf_exempt(DjangoApplication(Application([WebService],
        'soap.services',
        in_protocol=Soap11(),
        out_protocol=Soap11(),
    )))
