def removekey(d, key):
    r = dict(d)
    if r.get(key):
        del r[key]
    return r

def bkmk_to_code(bkmk):
    return {'codename': bkmk['content'], **removekey(bkmk, 'content')}
