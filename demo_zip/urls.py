# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.conf.urls import url
from demo_zip import views

urlpatterns = [
    url(r'^list/$', views.ListZipApplications.as_view(), name='list'),
    url(r'^upload/$', views.UploadZipApplication.as_view(), name='upload'),
    url(r'^update/(?P<pk>\d+)/$', views.UpdateZipApplication.as_view(), name='update'),
    url(r'^download/(?P<id>\d+)/$', views.DownloadZipApplication.as_view(), name='download'),
    url(r'^delete/(?P<pk>\d+)/$', views.DeleteZipApplication.as_view(), name='delete'),
]
