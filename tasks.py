from .etreeconv import root_dict_to_etree
from lxml import etree
from .settings import *
from .wic.wic_client_v2 import wic_client
from .utils import format_list_tag
from suds.client import Client

try:
    from jnius import autoclass as Java
    EncryptHandler = Java(ENCRYPT_CLASS_PATH)
except:
    pass

try:
    call_back_client = Client(CALL_BACK_WSDL, cache=None)
except:
    pass


#Install django-celery steps:
#pip install celery==2.4.7
#pip install django-celery==2.4.1

#Update your settings.py
'''
import djcelery
djcelery.setup_loader()
CELERY_RESULT_BACKEND = "amqp"
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"
CELERYD_WORKER_LOST_WAIT = 3600
CELERYD_TASK_TIME_LIMIT = 3600
INSTALLED_APPS += ('djcelery', )
'''
#Start django-celery worker
#python manage.py celeryd -l info
try:
    from celery.task import task
except:
    pass

@task
def _handle_request(method, params):
    try:
        print 'Request: ' + str(params)
        kwargs = params[method]
        c = wic_client()
        kwargs = getattr(c, method)(**kwargs)
        params[method] = kwargs
        res = params
        print 'Result:  ' + str(res)
        res = root_dict_to_etree({'response': res})
        res = etree.tostring(res, encoding='UTF-8', xml_declaration=True)
        res = format_list_tag(res)
        res = EncryptHandler.get_encrypt_by_password(res, ENCRYPT_PASSWORD)
        _call_back_result.delay(res)
    except Exception, exc:
        raise _handle_request.retry(exc=exc)

@task
def _call_back_result(result):
    try:
        print 'CallBack:' + result
        res = call_back_client.service.invoke(in0=result)
        print 'Response:' + res
    except Exception, exc:
        raise _call_back_result.retry(exc=exc)
