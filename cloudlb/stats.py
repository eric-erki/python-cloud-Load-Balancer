# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"

class Stats(object):
    def __init__(self, client, lbId=None):
        self.lbId = lbId
        if self.lbId:
            self.lbId = int(self.lbId)
            self.path = "/loadbalancers/%s/stats" % self.lbId

        self.client = client

    def get(self):
        ret = self.client.get("%s.json" % self.path)
        #return ret[1]['errorpage']['content']
        return ret[1]

