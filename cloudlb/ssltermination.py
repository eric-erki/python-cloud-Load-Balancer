# -*- encoding: utf-8 -*-
__author__ = "Jason Straw <jason.straw@rackspace.com>"

import cloudlb.errors

class SSLTermination(object):
    kwargs = {'port': 'securePort',
                   'enabled': 'enabled',
                   'secureonly': 'secureTrafficOnly',
                   'certificate': 'certificate',
                   'intermediate': 'intermediateCertificate',
                   'privatekey': 'privatekey'
                  }
        
    def __repr__(self):
        try:
            return "<SSLTermination: port %s>" % self.port
        except AttributeError:
            return "<SSLTermination: unconfigured>"

    def __init__(self, client, lbId=None):
        self.lbId = lbId
        if self.lbId:
            self.lbId = int(self.lbId)
            self.path = "/loadbalancers/%s/ssltermination" % self.lbId

        self.client = client
        self.get()

    def get(self):
        """Get dictionary of current LB settings.

    Returns None if SSL Termination is not configured.
    """
        try:
            ret = self.client.get("%s.json" % self.path)
        except cloudlb.errors.NotFound:
            return None
        sslt = ret[1]['sslTermination']
        for (skey, value) in sslt.iteritems():
            key = [k for (k, v) in self.kwargs.iteritems() if v == skey]
            try:
                setattr(self, key[0], value)
            except IndexError:
                print skey, repr(key)
                raise
        if 'intermediateCertificate' in sslt.keys():
            self.intermediate = sslt['intermediateCertificate']
        else:
            self.intermediate = None
        return self
        
    def update(self, **kwargs):
        """Update SSL Termination settings:
        
    Takes keyword args of items to update.  
    
    If you're updating the cert/key/intermediate certificate, 
    you must provide all 3 keywords.
    """
        body = {}
        for (key, value) in kwargs.iteritems():
            body[self.kwargs[key]] = value
            setattr(self, key, value)
        self._put(body)


    def add(self, port, privatekey, certificate, intermediate=None, enabled=True, secureonly=False):
        self.port = port
        self.enabled = enabled
        self.secureonly = secureonly
        self.privatekey = privatekey
        self.certificate = certificate
        self.intermediate = intermediate
        body = {'securePort': self.port, 'enabled': self.enabled, 'secureTrafficOnly': self.secureonly}
        body['privatekey'] = self.privatekey
        body['certificate'] = self.certificate
        if self.intermediate != None:
           body['intermediateCertificate'] = self.intermediate
        self._put(body)

    def _put(self, body):
        self.client.put(self.path, body=body)

    def delete(self):
        self.client.delete(self.path)
