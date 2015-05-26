# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from test_runs.views import TestRunViewSet
from results.views import TestResultViewSet
from results.views import TestRawResultViewSet
from tasks.views import TaskViewSet


router = routers.DefaultRouter()
router.register(r'test_runs', TestRunViewSet)
router.register(r'results', TestResultViewSet)
router.register(r'raw_results', TestRawResultViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
]
