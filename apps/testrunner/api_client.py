# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import ujson

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class ApiClient(object):
    @classmethod
    def __send_request(cls, uri, method, data=""):
        logger.info('Sending request ({}) to {}'.format(method.upper(), uri))
        logger.debug('Sending data: {}'.format(data))

        response = requests.request(
            method,
            uri,
            data=ujson.dumps(data),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json',
            }
        )

        logger.debug('Response (code: {0}): {1}'.format(response.status_code, response.content))

        response.raise_for_status()

        return response.json()

    @classmethod
    def post(cls, uri, data):
        return cls.__send_request(uri, 'post', data)

    @classmethod
    def put(cls, uri, data):
        return cls.__send_request(uri, 'put', data)

    @classmethod
    def get(cls, uri):
        return cls.__send_request(uri, 'get')

    @classmethod
    def delete(cls, uri):
        return cls.__send_request(uri, 'delete')
