#!/usr/bin/env python

from django.conf.urls.defaults import *
from core import views

urlpatterns = patterns('',
    url(r'^$', views.BlofView.as_view()),
    url(r'webservice/$', views.WebserviceView.as_view()),
)