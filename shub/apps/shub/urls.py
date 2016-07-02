from django.views.generic.base import TemplateView
from django.conf.urls import patterns, url
import shub.apps.shub.views as shub_views

urlpatterns = patterns('',

    # Containers
    url(r'^containers$', shub_views.all_containers, name="containers"),
    url(r'^containers/new$', shub_views.edit_container, name="new_container"),
    url(r'^containers/(?P<cid>.+?)/edit$',shub_views.edit_container,name='edit_container'),
    url(r'^containers/(?P<cid>.+?)/save$',shub_views.upload_container,name='upload_container'),

    # Container Collections
    url(r'^collections/containers/new$',shub_views.edit_container_collection,name='new_container_collection'),
    url(r'^collections/containers/(?P<cid>.+?)/$',shub_views.view_container_collection,name='container_collection_details'),
    url(r'^collections/containers/(?P<cid>.+?)/edit$',shub_views.edit_container_collection,name='edit_container_collection'),
    url(r'^collections/containers/my$',shub_views.my_container_collections,name='my_container_collections')

)
