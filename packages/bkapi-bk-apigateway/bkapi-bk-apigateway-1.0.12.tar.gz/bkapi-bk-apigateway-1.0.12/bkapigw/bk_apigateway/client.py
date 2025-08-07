# -*- coding: utf-8 -*-
"""API Gateway Client
"""
import json
import logging

import requests

from .conf import APP_CODE, AVAILABLE_COLLECTIONS, SECRET_KEY

logger = logging.getLogger(__name__)


class BaseClient(object):
    """Base client class for api"""

    @classmethod
    def setup_resources(cls, resources):
        cls.available_collections = resources

    def __init__(self, app_code=None, app_secret=None, headers=None, common_args=None, stage="prod", timeout=None):
        """
        :param str app_code: App code to use
        :param str app_secret: App secret to use
        :param dict headers: headers be sent to api
        :param dict common_args: Args that will apply to every request
        :param str stage: Stage for api gateway
        :param int timeout: timeout for request
        """

        self.app_code = app_code or APP_CODE
        self.app_secret = app_secret or SECRET_KEY
        self.headers = headers or {}
        self.common_args = common_args or {}
        self.stage = stage
        self.timeout = timeout
        self._cached_collections = {}
        self._log_warning()

    def _log_warning(self):
        _, _, api_name = __package__.partition(".")
        logger.warning(
            "%s is no longer maintained, recommend to use bkapi.%s as a replacement",
            __package__,
            api_name,
        )

    def set_stage(self, stage):
        """Change the value of stage

        :param str stage: Stage for api gateway
        """
        self.stage = stage

    def set_timeout(self, timeout):
        self.timeout = timeout

    def merge_params_data_with_common_args(self, method, params, data):
        """Add common args to params every request"""
        common_args = dict(app_code=self.app_code, **self.common_args)
        if method in ["GET", "HEAD"]:
            _params = common_args.copy()
            _params.update(params or {})
            params = _params
        elif method in ["POST", "PUT", "PATCH", "DELETE"]:
            _data = common_args.copy()
            _data.update(data or {})
            data = json.dumps(_data)
        return params, data

    def __getattr__(self, key):
        if key not in self.available_collections:
            return getattr(super(BaseClient, self), key)

        if key not in self._cached_collections:
            collection = self.available_collections[key]
            self._cached_collections[key] = collection(self)
        return self._cached_collections[key]

    def request(self, method, url, params=None, data=None, path_params=None, **kwargs):
        pass


class RequestAPIClient(BaseClient):
    def request(self, *args, **kwargs):
        # update headers
        headers = kwargs.pop("headers", {})
        headers.update(self.headers)

        return self._request(headers=headers, *args, **kwargs)

    def _request(self, method, url, params=None, data=None, **kwargs):
        """Send request direct"""
        params, data = self.merge_params_data_with_common_args(method, params, data)
        logger.debug("Calling %s %s with params=%s, data=%s", method, url, params, data)
        return requests.request(method, url, params=params, data=data, timeout=self.timeout, **kwargs)


RequestAPIClient.setup_resources(AVAILABLE_COLLECTIONS)
