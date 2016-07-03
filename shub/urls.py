"""shub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
"""
from django.conf.urls import include, url, patterns
from shub.apps.main import urls as main_urls
from shub.apps.shub import urls as shub_urls
from shub.apps.users import urls as user_urls
from django.contrib import admin

# Configure custom error pages
from django.conf.urls import ( handler404, handler500 )
handler404 = 'shub.apps.main.views.handler404'
handler500 = 'shub.apps.main.views.handler500'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(main_urls)),
    url(r'^', include(shub_urls)),
    url(r'^', include(user_urls))
]
