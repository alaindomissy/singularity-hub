from shub.apps.shub.forms import ContainerForm, ContainerCollectionForm, WorkflowForm, WorkflowCollectionForm
from shub.apps.shub.models import Container, ContainerCollection, Workflow, WorkflowCollection
from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.http.response import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from shub.settings import BASE_DIR, MEDIA_ROOT
from django.forms.models import model_to_dict
from django.utils import timezone
import datetime
import hashlib
import pandas
import uuid
import shutil
import numpy
import uuid
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
    keyargs = {'unique_id':cid}
    try:
        container = Container.objects.get(**keyargs)
    except Container.DoesNotExist:
        raise Http404
    else:
        return container

# get container collection
def get_container_collection(cid,request):
    keyargs = {'unique_id':cid}
    try:
        collection = ContainerCollection.objects.get(**keyargs)
    except ContainerCollection.DoesNotExist:
        raise Http404
    else:
        return collection

# get workflow
def get_workflow(wid,request):
    keyargs = {'unique_id':wid}
    try:
        workflow = Workflow.objects.get(**keyargs)
    except Workflow.DoesNotExist:
        raise Http404
    else:
        return workflow

# get workflow collection
def get_workflow_collection(wid,request):
    keyargs = {'unique_id':wid}
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
    context = {"card_selection":"all_containers"}
    return render(request, 'containers/all_containers.html', context)


# New container
def new_container(request):
    context = {"card_selection":"new_container"}
    return render(request, 'containers/new_container.html', context)


# Edit container
def edit_container(request,cid=None):

    # Here must determine if user owns container based on collection

    if cid:
        container = get_container(bid,request)
    else:
        container = Container()
        if request.method == "POST":
            form = ContainerForm(request.POST,instance=container)
            if form.is_valid():
                container = form.save(commit=False)
                container.save()
                return HttpResponseRedirect(container.get_absolute_url())
        else:
            form = ContainerForm(instance=container)

        context = {"form": form}
        return render(request, "containers/edit_container.html", context)
    return redirect("containers")

# Edit container collection
def edit_container_collection(request, cid=None):

    if cid:
        container = get_container(bid,request)
        is_owner = container.owner == request.user
    else:
        is_owner = True
        container = Container(owner=request.user)
        if request.method == "POST":
            form = ContainerForm(request.POST,instance=container)
            if form.is_valid():
                previous_contribs = set()
                if form.instance.unique_id is not None:
                    previous_contribs = set(form.instance.contributors.all())
                container = form.save(commit=False)
                container.save()

                if is_owner:
                    form.save_m2m()  # save contributors
                    current_contribs = set(container.contributors.all())
                    new_contribs = list(current_contribs.difference(previous_contribs))

                return HttpResponseRedirect(container.get_absolute_url())
        else:
            form = ContainerForm(instance=container)

        context = {"form": form,
                   "is_owner": is_owner}

        return render(request, "containers/edit_container.html", context)
    return redirect("containers")


