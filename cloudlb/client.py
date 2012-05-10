# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
import httplib2
import os
import sys
import json
import pprint
import time
import datetime

import cloudlb.base
import cloudlb.consts
import cloudlb.errors

class CLBClient(httplib2.Http):
    """
    Client class for accessing the CLB API.
    """

    def __init__(self,
                 username,
                 api_key,
                 region,
                 auth_url=None):
        super(CLBClient, self).__init__()
        self.username = username
        self.api_key = api_key

        if not auth_url and region == 'lon':
            auth_url = cloudlb.consts.UK_AUTH_SERVER
        else:
            auth_url = cloudlb.consts.DEFAULT_AUTH_SERVER
        self._auth_url = auth_url

        if region.lower() in cloudlb.consts.REGION.values():
            self.region = region
        elif region.lower() in cloudlb.consts.REGION.keys():
            self.region = cloudlb.consts.REGION[region]
        else:
            raise cloudlb.errors.InvalidRegion()

        self.auth_token = None
        self.account_number = None
        self.region_account_url = None

    def authenticate(self):
        headers = {'Content-Type': 'application/json'}
        body = '{"credentials": {"username": "%s", "key": "%s"}}' \
               % (self.username, self.api_key)
        response, body = self.request(self._auth_url, 'POST',
                                      body=body, headers=headers)

        auth_data = json.loads(body)['auth']

        # A status code of 401 indicates that the supplied credentials
        # were not accepted by the authentication service.
        if response.status == 401:
            raise cloudlb.errors.AuthenticationFailed()

        if response.status != 200:
            raise cloudlb.errors.ResponseError(response.status,
                                               response.reason)

        self.account_number = int(os.path.basename(
          auth_data['serviceCatalog']['cloudServers'][0]['publicURL']))
        self.auth_token = auth_data['token']['id']
        self.region_account_url = "%s/%s" % (
            cloudlb.consts.REGION_URL % (self.region),
            self.account_number)

    def _cloudlb_request(self, url, method, **kwargs):
        if not self.region_account_url:
            self.authenticate()

        #TODO: Look over
        # Perform the request once. If we get a 401 back then it
        # might be because the auth token expired, so try to
        # re-authenticate and try again. If it still fails, bail.
        kwargs.setdefault('headers', {})['X-Auth-Token'] = self.auth_token
        kwargs['headers']['User-Agent'] = cloudlb.consts.USER_AGENT
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['body'] = json.dumps(kwargs['body'])

        ext = ""
        fullurl = "%s%s%s" % (self.region_account_url, url, ext)

        #DEBUGGING:
        if 'PYTHON_CLOUDLB_DEBUG' in os.environ:
            pp = pprint.PrettyPrinter(stream=sys.stderr, indent=2)
            sys.stderr.write("URL: %s\n" % (fullurl))
            sys.stderr.write("ARGS: %s\n" % (str(kwargs)))
            sys.stderr.write("METHOD: %s\n" % (str(method)))
            if 'body' in kwargs:
                pp.pprint(json.loads(kwargs['body']))
        response, body = self.request(fullurl, method, **kwargs)

        if 'PYTHON_CLOUDLB_DEBUG' in os.environ:
            sys.stderr.write("RETURNED HEADERS: %s\n" % (str(response)))
        # If we hit a 413 (Request Limit) response code,
        # check to see how long we have to wait.
        # If you have to wait more then 10 seconds,
        # raise ResponseError with a more sane message then CLB provides
        if response.status == 413:
            now = datetime.datetime.strptime(response['date'],
                    '%a, %d %b %Y %H:%M:%S %Z')
            # Retry-After header now doesn't always return a timestamp, 
            # try parsing the timestamp, if that fails wait 5 seconds 
            # and try again.  If it succeeds figure out how long to wait
            try:
                retry = datetime.datetime.strptime(response['retry-after'],
                        '%a, %d %b %Y %H:%M:%S %Z')
            except ValueError:
                if response['retry-after'] > '30':
                    raise cloudlb.errors.ResponseError(response.status,
                        "Account is currently above limit, please wait %s seconds." % 
                        (response['retry-after']))
                else:
                    time.sleep(5)
                    response, body = self.request(fullurl, method, **kwargs)
            except:
                raise
            else:
                if (retry - now) > datetime.timedelta(seconds=10):
                    raise cloudlb.errors.ResponseError(response.status,
                        "Account is currently above limit, please wait %s seconds." % 
                        (retry - now))
                else:
                    time.sleep((retry - now).seconds)
                    response, body = self.request(fullurl, method, **kwargs)

        if body:
            try:
                body = json.loads(body, object_hook=lambda obj: dict((k.encode('ascii'), v) for k, v in obj.items()))
            except(ValueError):
                pass

            if 'PYTHON_CLOUDLB_DEBUG' in os.environ:
                sys.stderr.write("BODY:")
                pp.pprint(body)

        if response.status == 413:
            raise cloudlb.errors.ResponseError(response.status,
                    "Account is currently above limit, please wait until"
                    + retry + ".")
        elif response.status == 404:
            raise cloudlb.errors.NotFound(response.status, body['message'])
        elif (response.status < 200) or (response.status > 299):
            raise cloudlb.errors.ResponseError(response.status,
                                               response.reason)

        return response, body

    def put(self, url, **kwargs):
        return self._cloudlb_request(url, 'PUT', **kwargs)

    def get(self, url, **kwargs):
        return self._cloudlb_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cloudlb_request(url, 'POST', **kwargs)

    def delete(self, url, **kwargs):
        return self._cloudlb_request(url, 'DELETE', **kwargs)
