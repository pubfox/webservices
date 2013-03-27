from spyne.util.odict import odict

def clear_list(params):
    '''Change the list with single item to the item value'''
    if isinstance(params, dict) or isinstance(params, odict):
        for k, v in params.items():
            params[k] = clear_list(v)
    elif isinstance(params, list):
        if len(params) == 1:
            params = clear_list(params[0])
        elif len(params) > 1:
            for i, v in enumerate(params):
                params[i] = clear_list(v)
    return params

def get_method(params):
    '''Get the method key from params'''
    for k in params.keys():
        if k != 'company' and k != 'requestId':
            return k
    return None

def format_list_tag(xml):
    '''Format list element tag'''
    tags = ['<ipPermissions>', '</ipPermissions>']
    for tag in tags:
        old = '%s%s' % (tag, tag, )
        xml =  xml.replace(old, tag)
    return xml
