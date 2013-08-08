#!/usr/bin/env python

from django.conf.urls.defaults import *
from core import views

urlpatterns = patterns('',
    url(r'^$', views.BlofView.as_view()),
    url(r'webservice/$', views.WebserviceView.as_view()),
<<<<<<< HEAD
)
=======
)
>>>>>>> 34ccc4cc1fe7adc513a697f00d5b2a0cb157e3c8
