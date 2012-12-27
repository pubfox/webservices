from spyne.util.odict import odict

def clear_list(params):
    for k, v in params.items():
        if isinstance(v, list) and len(v) == 1:
            params[k] = v[0]
            if isinstance(v[0], dict) or isinstance(v[0], odict):
                params[k] = clear_list(v[0])
    return params
