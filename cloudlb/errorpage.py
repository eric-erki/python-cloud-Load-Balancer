# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"

class ErrorPage(object):
    def __repr__(self):
        return "<ErrorPage>"

    def __init__(self, client, lbId=None):
        self.lbId = lbId
        if self.lbId:
            self.lbId = int(self.lbId)
            self.path = "/loadbalancers/%s/errorpage" % self.lbId

        self.client = client

    def get(self):
        ret = self.client.get("%s.json" % self.path)
        return ret[1]['errorpage']['content']

    def add(self, html):
        body = {'errorpage': {'content': html}}
        self.client.put(self.path, body=body)

    def delete(self):
        self.client.delete(self.path)
