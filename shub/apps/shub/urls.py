from django.views.generic.base import TemplateView
from django.conf.urls import patterns, url
import shub.apps.shub.views as shub_views

urlpatterns = patterns('',
    url(r'^containers$', shub_views.all_containers, name="containers"),
    url(r'^containers/new$', shub_views.new_container, name="new_container")
)