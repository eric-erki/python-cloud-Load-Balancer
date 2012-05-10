# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
from cloudlb import base
from cloudlb.consts import LB_PROTOCOLS, LB_ATTRIBUTES_MODIFIABLE
from cloudlb.errors import InvalidProtocol, InvalidLoadBalancerName
from cloudlb.node import Node, NodeDict
from cloudlb.virtualip import VirtualIP
from cloudlb.usage import get_usage
from cloudlb.stats import Stats
from cloudlb.accesslist import AccessList
from cloudlb.healthmonitor import HealthMonitorManager
from cloudlb.sessionpersistence import SessionPersistenceManager
from cloudlb.connectionlogging import ConnectionLogging
from cloudlb.connectionthrottle import ConnectionThrottleManager
from cloudlb.errorpage import ErrorPage
from cloudlb.ssltermination import SSLTermination

class LoadBalancer(base.Resource):
    accessList = None
    sessionPersistence = None
    healthMonitor = None

    def __repr__(self):
        return "<LoadBalancer: %s>" % self.name

    def delete(self):
        """
        Delete Load Balancer..
        """
        self.manager.delete(self)

    def _add_details(self, info):
        for (k, v) in info.iteritems():
            if k == "nodes":
                v = NodeDict([Node(parent=self, **x) for x in v])

            if k == "sessionPersistence":
                v = v['persistenceType']

            if k == "cluster":
                v = v['name']

            if k == "virtualIps":
                v = [VirtualIP(parent=self, **x) for x in v]

            if k in ('created', 'updated'):
                v = base.convert_iso_datetime(v['time'])

            setattr(self, k, v)

    def add_nodes(self, nodes):
        resp, body = self.manager.add_nodes(self.id, nodes)
        return [Node(parent=self, **x) for x in body['nodes']]

    def update(self):
        self.manager.update(self, self._info, self.__dict__)

    def get_usage(self, startTime=None, endTime=None):
        startTime = startTime and startTime.isoformat()
        endTime = endTime and endTime.isoformat()
        ret = get_usage(self.manager.api.client, lbId=base.getid(self),
                        startTime=startTime, endTime=endTime)
        return ret

    def get_stats(self):
        stats = Stats(self.manager.api.client, base.getid(self))
        return stats.get() 

    def accesslist(self):
        accesslist = AccessList(self.manager.api.client, base.getid(self))
        return accesslist

    def healthmonitor(self):
        hm = HealthMonitorManager(self.manager.api.client, base.getid(self))
        return hm

    def session_persistence(self):
        sm = SessionPersistenceManager(
            self.manager.api.client, base.getid(self))
        return sm

    def errorpage(self):
        errorpage = ErrorPage(self.manager.api.client, base.getid(self))
        return errorpage

    def connection_logging(self):
        cm = ConnectionLogging(
            self.manager.api.client, base.getid(self))
        return cm

    #TODO: Not working!
    def connection_throttling(self):
        ctm = ConnectionThrottleManager(
            self.manager.api.client, base.getid(self),
        )
        return ctm

    def ssl_termination(self):
        sslt = SSLTermination(self.manager.api.client, base.getid(self))
        return sslt


class LoadBalancerManager(base.ManagerWithFind):
    resource_class = LoadBalancer

    def get(self, loadbalancerid):
        """
        Get a Load Balancer.

        :param loadbalancerid: ID of the :class:`LoadBalancer` to get.
        :rtype: :class:`LoadBalancer`
        """
        return self._get("/loadbalancers/%s.json" % \
                      base.getid(loadbalancerid), "loadBalancer")

    def list(self):
        """
        Get a list of loadbalancers.
        :rtype: list of :class:`LoadBalancer`

        Arguments:
        """
        return [x for x in \
                    self._list("/loadbalancers.json", "loadBalancers") \
                 if x._info['status'] != "DELETED"]

    def search(self, ip):
        """
        Get a list of loadbalancers who are balancing traffic to `ip`.
        The loadbalancer details are not as complete as the list() call,
        only name, status and id are returned.
        """
        return [x for x in \
                    self._list("/loadbalancers.json?nodeaddress=%s" % ip, 
                        "loadBalancers")]
        

    def create(self, name, port,
               protocol, nodes, virtualIps, algorithm='RANDOM'):
        """
        Create a new loadbalancer.

        #TODO: Args
        """

        if not protocol in LB_PROTOCOLS:
            raise InvalidProtocol("''%s'' is not a valid protocol" % \
                                      (protocol))

        nodeDico = [x.toDict() for x in nodes]
        vipDico = [x.toDict() for x in virtualIps]

        if len(name) > 128:
            raise InvalidLoadBalancerName("LB name is too long.")

        body = {"loadBalancer": {
            "name": name,
            "port": base.getid(port),
            "protocol": protocol,
            "nodes": nodeDico,
            "virtualIps": vipDico,
            "algorithm": algorithm,
            }}

        return self._create("/loadbalancers", body, "loadBalancer")

    def delete(self, loadbalancerid):
        """
        Delete load balancer.

        :param loadbalancerid: ID of the :class:`LoadBalancer` to get.
        :rtype: :class:`LoadBalancer`
        """
        self._delete("/loadbalancers/%s" % base.getid(loadbalancerid))

    def add_nodes(self, loadBalancerId, nodes):
        nodeDico = [x.toDict() for x in nodes]
        resp, body = self.api.client.post('/loadbalancers/%d/nodes' % (
                            base.getid(loadBalancerId)
                            ), body={"nodes": nodeDico})
        return (resp, body)

    def delete_node(self, loadBalancerId, nodeId):
        self.api.client.delete('/loadbalancers/%d/nodes/%d' % (
                base.getid(loadBalancerId),
                base.getid(nodeId),
                ))

    def update_node(self, loadBalancerId, nodeId, dico):
        self.api.client.put('/loadbalancers/%d/nodes/%d' % (
                base.getid(loadBalancerId),
                base.getid(nodeId),
                ), body={"node": dico})

    def update(self, lb, originalInfo, info):
        ret = {}
        for k in LB_ATTRIBUTES_MODIFIABLE:
            if k in originalInfo and info[k] != originalInfo[k]:
                ret[k] = info[k]

        if 'protocol' in ret.keys() and ret['protocol'] not in LB_PROTOCOLS:
            raise InvalidProtocol("''%s'' is not a valid protocol" % \
                                      (ret['protocol']))

        if not ret:
            #TODO: proper Exceptions:
            raise Exception("Nothing to update.")

        self.api.client.put('/loadbalancers/%s' % base.getid(lb), body=ret)

