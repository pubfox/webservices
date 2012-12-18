from spyne.application import Application
from spyne.decorator import srpc, rpc
from spyne.protocol.soap import Soap11
from spyne.protocol.http import HttpRpc
from spyne.service import ServiceBase
from spyne.model.complex import Array, Iterable, ComplexModel
from spyne.model.primitive import Integer, Float, Unicode, Boolean, String
from spyne.server.django import DjangoApplication

from django.views.decorators.csrf import csrf_exempt
from .response_types import *

from horizon import api
from glance import client as glance_client
from keystoneclient.v2_0 import client as keystone_client
from novaclient.v1_1 import client as nova_client

class WebService(ServiceBase):
    @srpc(Integer, Unicode, _returns=User)
    def get_user(userid, username):
        res = User(userid=userid, username=username)
        return res

soap_services = csrf_exempt(DjangoApplication(Application([WebService],
        'soap.services',
        #in_protocol=Soap11(),
        in_protocol=HttpRpc(), #For test
        out_protocol=Soap11(),
    )))
