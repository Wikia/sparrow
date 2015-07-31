# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps
import ujson

def post_response(f):
    """Decorator to mock API POST using response library (requires @response.activate)"""
    @wraps(f)
    def post_wrapper(self, *args, **kwargs):
        # callback to mock API response
        def request_callback(request):
            api_response = self.client.post(request.url, data=ujson.decode(request.body), headers=request.headers)
            self.response_data = api_response.data

            return api_response.status_code, {}, api_response.content

        kwargs['post_callback'] = request_callback
        f(self, *args, **kwargs)

    return post_wrapper

def put_response(f):
    """Decorator to mock API PUT using response library (requires @response.activate)"""
    @wraps(f)
    def put_wrapper(self, *args, **kwargs):
        # callback to mock API response
        def request_callback(request):
            api_response = self.client.put(request.url, data=ujson.decode(request.body), headers=request.headers)
            self.response_data = api_response.data

            return api_response.status_code, {}, api_response.content

        kwargs['put_callback'] = request_callback
        f(self, *args, **kwargs)

    return put_wrapper

def get_response(f):
    """Decorator to mock API GET using response library (requires @response.activate)"""
    @wraps(f)
    def get_wrapper(self, *args, **kwargs):
        # callback to mock API response
        def request_callback(request):
            api_response = self.client.get(request.url, data=ujson.decode(request.body), headers=request.headers)
            self.response_data = api_response.data

            return api_response.status_code, {}, api_response.content

        kwargs['get_callback'] = request_callback
        f(self, *args, **kwargs)

    return get_wrapper

def delete_response(f):
    """Decorator to mock API DELETE using response library (requires @response.activate)"""
    @wraps(f)
    def delete_wrapper(self, *args, **kwargs):
        # callback to mock API response
        def request_callback(request):
            api_response = self.client.delete(request.url, data=ujson.decode(request.body), headers=request.headers)
            self.response_data = api_response.data

            return api_response.status_code, {}, api_response.content

        kwargs['delete_callback'] = request_callback
        f(self, *args, **kwargs)

    return delete_wrapper

def patch_response(f):
    """Decorator to mock API PATCH using response library (requires @response.activate)"""
    @wraps(f)
    def post_wrapper(self, *args, **kwargs):
        # callback to mock API response
        def request_callback(request):
            api_response = self.client.patch(request.url, data=ujson.decode(request.body), headers=request.headers)
            self.response_data = api_response.data

            return api_response.status_code, {}, api_response.content

        kwargs['patch_callback'] = request_callback
        f(self, *args, **kwargs)

    return patch_wrapper

