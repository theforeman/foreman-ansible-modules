# -*- coding: utf-8 -*-

# pylint: disable=raise-missing-from
# pylint: disable=super-with-arguments

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import json
from ansible.module_utils._text import to_native
from ansible.module_utils import six
from ansible.module_utils.urls import Request
try:
    from ansible.module_utils.urls import prepare_multipart
except ImportError:
    def prepare_multipart(fields):
        raise NotImplementedError


class RequestResponse(object):
    def __init__(self, resp):
        self._resp = resp

    @property
    def status_code(self):
        if hasattr(self._resp, 'status'):
            status = self._resp.status
        else:
            status = self._resp.getcode()
        return status

    @property
    def headers(self):
        return self._resp.headers

    @property
    def url(self):
        if hasattr(self._resp, 'url'):
            url = self._resp.url
        else:
            url = self._resp.geturl()
        return url

    @property
    def reason(self):
        if hasattr(self._resp, 'reason'):
            reason = self._resp.reason
        else:
            reason = ""
        return reason

    def raise_for_status(self):
        http_error_msg = ""

        if 400 <= self.status_code < 500:
            http_error_msg = "{0} Client Error: {1} for url: {2}".format(self.status_code, self.reason, self.url)
        elif 500 <= self.status_code < 600:
            http_error_msg = "{0} Server Error: {1} for url: {2}".format(self.status_code, self.reason, self.url)

        if http_error_msg:
            raise Exception(http_error_msg)

    def json(self, **kwargs):
        return json.loads(to_native(self._resp.read()), **kwargs)


class RequestSession(Request):
    @property
    def auth(self):
        return (self.url_username, self.url_password)

    @auth.setter
    def auth(self, value):
        self.url_username, self.url_password = value
        self.force_basic_auth = True

    @property
    def verify(self):
        return self.validate_certs

    @verify.setter
    def verify(self, value):
        self.validate_certs = value

    def request(self, method, url, **kwargs):
        validate_certs = kwargs.pop('verify', None)
        params = kwargs.pop('params', None)
        if params:
            url += '?' + six.moves.urllib.parse.urlencode(params)
        headers = kwargs.pop('headers', None)
        data = kwargs.pop('data', None)
        if data:
            if not isinstance(data, six.string_types):
                data = six.moves.urllib.parse.urlencode(data, doseq=True)
        files = kwargs.pop('files', None)
        if files:
            ansible_files = {k: {'filename': v[0], 'content': v[1].read(), 'mime_type': v[2]} for (k, v) in files.items()}
            _content_type, data = prepare_multipart(ansible_files)
        if 'json' in kwargs:
            # it can be `json=None`…
            data = json.dumps(kwargs.pop('json'))
            if headers is None:
                headers = {}
            headers['Content-Type'] = 'application/json'
        result = self.open(method, url, validate_certs=validate_certs, data=data, headers=headers, **kwargs)
        return RequestResponse(result)
