# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"

import cloudlb.consts

class CloudlbException(Exception): pass

class ResponseError(CloudlbException):
    """
    Raised when the remote service returns an error.
    """
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
        Exception.__init__(self)

    def __str__(self):
        return '%d: %s' % (self.status, self.reason)

    def __repr__(self):
        return '%d: %s' % (self.status, self.reason)

class RateLimit(ResponseError):
    """
    Raised when too many requests have been made 
    of the remote service in a given time period.
    """
    status = 413
    
    def __init__(self, wait):
        self.wait = wait
        self.reason = "Account is currently above limit, please wait %s seconds." % (wait)
        Exception.__init__(self)

class AbsoluteLimit(ResponseError):
    """
    Raised when an absolute limit is reached. Absolute limits include the
    number of load balancers in a region, the number of nodes behind a load
    balancer.
    """
    status = 413
    def __init__(self, reason):
        self.reason = reason
        Exception.__init__(self)

class BadRequest(ResponseError):
    """
    Raised when the request doesn't match what was anticipated.
    """
    pass

# Immutable and Unprocessable Entity are both 422 errors, but have slightly different meanings
class ImmutableEntity(ResponseError):
    pass

class UnprocessableEntity(ResponseError):
    pass

class InvalidRegion(CloudlbException):
    """
    Raised when the region specified is invalid
    """
    regions = cloudlb.consts.REGION.values() + cloudlb.consts.REGION.keys()
    def __init__(self, region):
        self.region = region
        Exception.__init__(self)

    def __str__(self):
        return 'Region %s not in active region list: %s' % (self.region, ', '.join(self.regions))

    def __repr__(self):
        return 'Region %s not in active region list: %s' % (self.region, ', '.join(self.regions))

class InvalidProtocol(CloudlbException):
    """
    Raised when the protocol specified is invalid
    """
    pass


class AuthenticationFailed(ResponseError):
    """
    Raised on a failure to authenticate.
    """
    pass


class NotFound(ResponseError):
    """
    Raised when there the object wasn't found.
    """
    pass

class InvalidLoadBalancerName(CloudlbException):
    def __init__(self, reason):
        self.reason = reason
        Exception.__init__(self)

    def __str__(self):
        return '%s' % (self.reason)

    def __repr__(self):
        return '%s' % (self.reason)
