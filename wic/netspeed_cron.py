from wic_client_v2 import wic_client
def netspeed_cron():
    c = wic_client()
    instances = c.client.servers.list(search_opts={'status':'ACTIVE'})
    for instance in instances:
        netspeed = instance.metadata.get('netspeed', None)
        if netspeed:
            try:
                print c._netspeed_update(instance, netspeed)
            except Exception, e:
                print e.message or e.reason

if __name__ == '__main__':
    netspeed_cron()