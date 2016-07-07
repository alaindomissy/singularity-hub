from shub.apps.shub.forms import ContainerForm, ContainerCollectionForm, WorkflowForm, WorkflowCollectionForm
from shub.apps.shub.models import Container, ContainerCollection, Workflow, WorkflowCollection
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.http.response import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.exceptions import PermissionDenied, ValidationError
from shub.apps.shub.utils import save_image_upload
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from shub.settings import BASE_DIR, MEDIA_ROOT
from django.forms.models import model_to_dict
from django.utils import timezone
from django.contrib import messages
import traceback
import datetime
import tarfile
import tempfile
import pickle
import zipfile
import hashlib
import pandas
import uuid
import shutil
import numpy
import uuid
import gzip
import json
import csv
import re
import os

media_dir = os.path.join(BASE_DIR,MEDIA_ROOT)

### AUTHENTICATION ####################################################

# need functions here to check permissions of things, after add users


#### GETS #############################################################

# get container
def get_container(cid,request):
    keyargs = {'id':cid}
    try:
        container = Container.objects.get(**keyargs)
    except Container.DoesNotExist:
        raise Http404
    else:
        return container

# get container collection
def get_container_collection(cid,request):
    keyargs = {'id':cid}
    try:
        collection = ContainerCollection.objects.get(**keyargs)
    except ContainerCollection.DoesNotExist:
        raise Http404
    else:
        return collection

# get workflow
def get_workflow(wid,request):
    keyargs = {'id':wid}
    try:
        workflow = Workflow.objects.get(**keyargs)
    except Workflow.DoesNotExist:
        raise Http404
    else:
        return workflow

# get workflow collection
def get_workflow_collection(wid,request):
    keyargs = {'id':wid}
    try:
        collection = WorkflowCollection.objects.get(**keyargs)
    except WorkflowCollection.DoesNotExist:
        raise Http404
    else:
        return collection


###############################################################################################
# CONTAINERS ##################################################################################
###############################################################################################

# All containers
def all_containers(request):
    has_collections = False
    collections = ContainerCollection.objects.filter(private=False)
    context = {"collections":collections,
               "page_title":"Container Collections"}
    return render(request, 'containers/all_containers.html', context)

# Personal collections
@login_required
def my_container_collections(request):
    collections = ContainerCollection.objects.filter(owner=request.user)
    context = {"collections":collections,
               "page_title":"My Container Collections"}
    return render(request, 'containers/all_containers.html', context)

# View container collection
@login_required
def view_container_collection(request,cid):
    collection = get_container_collection(cid,request)
    containers = Container.objects.filter(collection=collection)
    workflows = WorkflowCollection.objects.filter(owner=request.user)
    context = {"collection":collection,
               "containers":containers,
               "workflows":workflows}
    return render(request, 'containers/container_collection_details.html', context)

# View container
@login_required
def view_container(request,cid):
    container = get_container(cid,request)
    context = {"container":container}
    return render(request, 'containers/container_details.html', context)

# Delete container
@login_required
def delete_container(request,cid):
    container = get_container(cid,request)
    collection = container.collection
    if request.user == collection.owner:
        if container.image.file != None:
            file_path = container.image.file.name
            if os.path.exists(file_path):
                os.remove(file_path)
        container.delete()
    else:
        # If not authorizer, alert!
        msg = "You are not authorized to perform this operation."
        messages.warning(request, msg)
    return HttpResponseRedirect(collection.get_absolute_url())
    
# Edit container
@login_required
def edit_container(request,coid,cid=None):

    # TODO: Add collaborators checking
    collection = get_container_collection(coid,request)
    if collection.owner == request.user:
        container = Container()
        if request.method == "POST" and cid != None:
            container = get_container(request,cid)
            form = ContainerForm(request.POST,instance=container)
            if form.is_valid():
                container = form.save(commit=False)
                container.save()
                return HttpResponseRedirect(container.get_absolute_url())
        else:
            form = ContainerForm(instance=container)
            context = {"form": form,
                       "collection": collection}
            return render(request, "containers/edit_container.html", context)
    return redirect("container_collections")


# Edit container collection
@login_required
def edit_container_collection(request, cid=None):

    if cid:
        collection = get_container_collection(cid,request)
        is_owner = collection.owner == request.user
    else:
        is_owner = True
        collection = ContainerCollection(owner=request.user)
        if request.method == "POST":
            form = ContainerCollectionForm(request.POST,instance=collection)
            if form.is_valid():
                previous_contribs = set()
                if form.instance.id is not None:
                    previous_contribs = set(form.instance.contributors.all())
                collection = form.save(commit=False)
                collection.save()

                if is_owner:
                    form.save_m2m()  # save contributors
                    current_contribs = set(collection.contributors.all())
                    new_contribs = list(current_contribs.difference(previous_contribs))

                return HttpResponseRedirect(collection.get_absolute_url())
        else:
            form = ContainerCollectionForm(instance=collection)

        context = {"form": form,
                   "is_owner": is_owner}

        return render(request, "containers/edit_container_collection.html", context)
    return redirect("container_collections")

# Upload container
@login_required
def upload_container(request,cid):
    collection = get_container_collection(cid,request)
    is_owner = collection.owner == request.user
    
    if is_owner:
        allowed_extensions = ['.img']
        if request.method == 'POST':
            form = ContainerForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    if 'image' in request.FILES:
                        # DO PARSING OF CONTAINER META FROM HEADER HERE
                        # Save image file to server, and to new container model
                        container = save_image_upload(collection,request.FILES['image'])
                    else:
                        raise Exception("Unable to find uploaded files.")
                except:
                    error = traceback.format_exc().splitlines()
                    msg = "An error occurred with this upload: {}".format(error)
                    messages.warning(request, msg)
                    return HttpResponseRedirect(collection.get_absolute_url())
                return HttpResponseRedirect(collection.get_absolute_url())
        else:
            form = ContainerForm()
            context = {"form": form,
                       "collection": collection}
            return render(request, "containers/edit_container.html", context)


###############################################################################################
# WORKFLOWS ###################################################################################
###############################################################################################

# All workflows
def all_workflows(request):
    has_collections = False
    collections = WorkflowCollection.objects.filter(private=False)
    context = {"collections":collections,
               "page_title":"Workflow Collections"}
    return render(request, 'workflows/all_workflows.html', context)

# Personal collections
@login_required
def my_workflow_collections(request):
    collections = WorkflowCollection.objects.filter(owner=request.user)
    context = {"collections":collections,
               "page_title":"My Workflow Collections"}
    return render(request, 'workflows/all_workflows.html', context)

# View workflow collection
@login_required
def view_workflow_collection(request,wid):
    collection = get_workflow_collection(wid,request)
    workflows = Workflow.objects.filter(collection=collection)
    context = {"collection":collection,
               "workflows":workflows}
    return render(request, 'workflows/workflow_collection_details.html', context)

# View workflow
@login_required
def view_workflow(request,wid):
    workflow = get_workflow(wid,request)
    context = {"workflow":workflow}
    return render(request, 'workflows/workflow_details.html', context)

# Delete workflow
@login_required
def delete_workflow(request,wid):
    workflow = get_workflow(wid,request)
    collection = workflow.collection
    if request.user == collection.owner:
        workflow.delete()
    else:
        # If not authorizer, alert!
        msg = "You are not authorized to perform this operation."
        messages.warning(request, msg)
    return HttpResponseRedirect(collection.get_absolute_url())
   

# Edit workflow
@login_required
def edit_workflow(request,coid,wid=None):

    # TODO: Add collaborators checking
    collection = get_workflow_collection(coid,request)
    if collection.owner == request.user:   
        workflow = Workflow()
        if request.method == "POST":
            form = WorkflowForm(request.POST,instance=workflow)
            if form.is_valid():
                workflow = form.save(commit=False)
                workflow.collection = collection
                workflow.save()
                return HttpResponseRedirect(workflow.get_absolute_url())
        else:
            form = WorkflowForm(instance=workflow)

            # Limit containers to those that are in public collections
            form.fields["containers"].queryset = Container.objects.filter(collection__private=False)

            context = {"form": form,
                       "collection": collection}
            return render(request, "workflows/edit_workflow.html", context)
    return redirect("workflow_collections")


# Edit container collection
@login_required
def edit_workflow_collection(request,coid=None):

    if coid:
        collection = get_workflow_collection(coid,request)
        is_owner = collection.owner == request.user
    else:
        is_owner = True
        collection = WorkflowCollection(owner=request.user)
        if request.method == "POST":
            form = WorkflowCollectionForm(request.POST,instance=collection)
            if form.is_valid():
                previous_contribs = set()
                if form.instance.id is not None:
                    previous_contribs = set(form.instance.contributors.all())
                collection = form.save(commit=False)
                collection.save()

                if is_owner:
                    form.save_m2m()  # save contributors
                    current_contribs = set(collection.contributors.all())
                    new_contribs = list(current_contribs.difference(previous_contribs))

                return HttpResponseRedirect(collection.get_absolute_url())
        else:
            form = WorkflowCollectionForm(instance=collection)

        context = {"form": form,
                   "is_owner": is_owner}

        return render(request, "workflows/edit_workflow_collection.html", context)
    return redirect("workflow_collections")

