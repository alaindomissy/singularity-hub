from django.views.generic.base import TemplateView
from django.conf.urls import patterns, url
import shub.apps.shub.views as shub_views

urlpatterns = patterns('',

    # Containers
    url(r'^containers$', shub_views.all_containers, name="container_collections"),
    url(r'^containers/(?P<coid>.+?)/new$', shub_views.edit_container, name="new_container"),
    url(r'^containers/(?P<coid>.+?)/(?P<cid>.+?)/edit$',shub_views.edit_container,name='edit_container'),
    url(r'^containers/(?P<cid>.+?)/$',shub_views.view_container,name='container_details'),
    url(r'^containers/(?P<cid>.+?)/save$',shub_views.upload_container,name='upload_container'),

    # Container Collections
    url(r'^collections/containers/new$',shub_views.edit_container_collection,name='new_container_collection'),
    url(r'^collections/containers/(?P<cid>.+?)/$',shub_views.view_container_collection,name='container_collection_details'),
    url(r'^collections/containers/(?P<cid>.+?)/edit$',shub_views.edit_container_collection,name='edit_container_collection'),
    url(r'^collections/containers/my$',shub_views.my_container_collections,name='my_container_collections'),

    # Workflows
    url(r'^workflows$', shub_views.all_workflows, name="workflow_collections"),
    url(r'^workflows/(?P<coid>.+?)/new$', shub_views.edit_workflow, name="new_workflow"),
    url(r'^workflows/(?P<coid>.+?)/(?P<wid>.+?)/edit$',shub_views.edit_workflow,name='edit_workflow'),
    url(r'^workflows/(?P<coid>.+?)/add$', shub_views.add_workflow, name="add_workflow"),
    url(r'^workflows/(?P<wid>.+?)/$',shub_views.view_workflow,name='workflow_details'),

    # Workflow Collections
    url(r'^collections/workflows/new$',shub_views.edit_workflow_collection,name='new_workflow_collection'),
    url(r'^collections/workflows/(?P<wid>.+?)/$',shub_views.view_workflow_collection,name='workflow_collection_details'),
    url(r'^collections/workflows/(?P<coid>.+?)/edit$',shub_views.edit_workflow_collection,name='edit_workflow_collection'),
    url(r'^collections/workflows/my$',shub_views.my_workflow_collections,name='my_workflow_collections')

)
