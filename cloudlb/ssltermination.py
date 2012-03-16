# -*- encoding: utf-8 -*-
__author__ = "Jason Straw <jason.straw@rackspace.com>"

class SSLTermination(object):
    self.kwargs = {'port': 'securePort',
                   'enabled': 'enabled',
                   'secureonly': 'secureTrafficOnly',
                   'certificate': 'certificate',
                   'intermediate': 'intermediateCertificate',
                   'privatekey': 'privatekey'
                  }
        
    def __repr__(self):
        return "<SSLTermination: port %s>" % self.port

    def __init__(self, client, lbId=None):
        self.lbId = lbId
        if self.lbId:
            self.lbId = int(self.lbId)
            self.path = "/loadbalancers/%s/ssltermination" % self.lbId

        self.client = client

    def get(self):
        ret = self.client.get("%s.json" % self.path)
        sslt = ret[1]
        for (key, value) in sslt.iteritems():
            key = [k for k, v in self.kwargs.iteritems() if v == value][0]
            setattr(self, key, value)
        if 'intermediateCertificate' in sslt.keys():
            self.intermediate = sslt_json_to_pem(sslt['intermediateCertificate'])
        else:
            self.intermediate = None
        return self
        
    def update(self, **kwargs):
        body = {}
        for (key, value) in kwargs.iteritems():
            body[self.kwargs[key]] = value
            setattr(self, key, value)
        self._put(body)


    def add(self, port, privatekey, certificate, intermediate=None, enabled=True, secureonly=True):
        self.port = port
        self.enabled = enabled
        self.secureonly = secureonly
        self.privatekey = privatekey
        self.certificate = certificate
        self.intermediate = intermediate
        body = {'securePort': self.port, 'enabled': self.enabled, 'secureTrafficOnly': self.secureonly}
        body['privatekey'] = self._pem_to_json(self.privatekey)
        body['certificate'] = self._pem_to_json(self.certificate)
        if self.intermediate != None:
           body['intermediateCertificate'] = self._pem_to_json(self.intermediate)
        self._put(self, body)

    def _put(self, body):
        self.client.put(self.path, body=body)

    def delete(self):
        self.client.delete(self.path)
