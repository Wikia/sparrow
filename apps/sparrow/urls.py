# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from tests.views import TestViewSet
from results.views import TestResultViewSet
from tasks.views import TaskViewSet


router = routers.DefaultRouter()
router.register(r'tests', TestViewSet)
router.register(r'results', TestResultViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
