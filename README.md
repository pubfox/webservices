webservices
===============================

A reusable django webservices app.

How to install
==============

1. Clone this app into your django project as an app.
2. Update your django project settings.py to add webservices app.
3. Update your django project urls.py to serve the webservice requests.
4. Restart your django server.

settings.py 
===========
```python
INSTALLED_APPS += ('webservices', )
```

urls.py
=======
```python
urlpatterns = patterns('',
    url(r'^soap/','webservices.views.soap_services', name='soap_services'), #Added here
)
```

Test
====
wsdl: 
```python
http://yourhost/soap/?wsdl
```
rpc: 
```python
http://yourhost/soap/get_user?userid=1&username=Tom
```
soap:
```python
from suds.client import Client
client = Client(url='http://yourhost/soap/?wsdl')
print client
print client.service.get_user(userid=1, username='Tom')
```



