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
    keyargs = {'unique_id':wid}
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
    if request.user.is_authenticated:
        if ContainerCollection.objects.count() > 0:
            has_collections = True
    context = {"has_collections":has_collections}
    return render(request, 'containers/all_containers.html', context)

# Personal collections
@login_required
def my_container_collections(request):
    collections = ContainerCollection.objects.filter(owner=request.user)
    context = {"collections":collections}
    return render(request, 'containers/my_container_collections.html', context)

# View container collection
@login_required
def view_container_collection(request,cid):
    collection = get_container_collection(cid,request)
    context = {"collection":collection}
    return render(request, 'containers/container_collection_details.html', context)


# View container
@login_required
def view_container(request,cid):
    container = get_container(cid,request)
    context = {"container":container}
    return render(request, 'containers/container_details.html', context)

# Edit container
@login_required
def edit_container(request,coid,cid=None):

    # TODO: Add collaborators checking
    collection = get_container_collection(coid,request)
    if collection.owner == request.user:

        if cid:
            container = get_container(cid,request)
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

            context = {"form": form,
                       "collection": collection}
            return render(request, "containers/edit_container.html", context)
    return redirect("containers")


# Edit container collection
@login_required
def edit_container_collection(request, cid=None):

    if cid:
        collection = get_container_collection(cid,request)
        is_owner = container.owner == request.user
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
                   "is_owner": is_owner,
                   "containers":"anything"}

        return render(request, "containers/edit_container_collection.html", context)
    return redirect("collections")

# Upload container
@login_required
def upload_container(request,cid):
    collection = get_container_collection(collection_cid,request)
    is_owner = collection.owner == request.user
    
    if is_owner:
        allowed_extensions = ['.img']
        niftiFiles = []
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                tmp_directory = tempfile.mkdtemp()
                try:
                    # Save archive (.zip or .tar.gz) to disk
                    if "file" in request.FILES:
                        archive_name = request.FILES['file'].name
                        _, archive_ext = os.path.splitext(archive_name)
                        if archive_ext == '.zip':
                            compressed = zipfile.ZipFile(request.FILES['file'])
                        elif archive_ext == '.gz':
                            django_file = request.FILES['file']
                            django_file.open()
                            compressed = tarfile.TarFile(fileobj=gzip.GzipFile(fileobj=django_file.file, mode='r'), mode='r')
                        else:
                            raise Exception("Unsupported archive type %s."%archive_name)
                        compressed.extractall(path=tmp_directory)
                    else:
                        raise Exception("Unable to find uploaded files.")


                    for label,fpath in niftiFiles:
                        nii = nib.load(fpath)
                        if len(nii.get_shape()) > 3 and nii.get_shape()[3] > 1:
                            messages.warning(request, "Skipping %s - not a 3D file."%label)
                            continue
                        hdr = nii.get_header()
                        raw_hdr = hdr.structarr

                        path, name, ext = split_filename(fpath)
                        dname = name + ".nii.gz"
                        spaced_name = name.replace('_',' ').replace('-',' ')

                        if ext.lower() != ".nii.gz":
                            new_file_tmp_dir = tempfile.mkdtemp()
                            new_file_tmp = os.path.join(new_file_tmp_dir, name) + '.nii.gz'
                            nib.save(nii, new_file_tmp)
                            f = ContentFile(open(new_file_tmp).read(), name=dname)
                            shutil.rmtree(new_file_tmp_dir)
                            label += " (old ext: %s)" % ext
                        else:
                            f = ContentFile(open(fpath).read(), name=dname)

                        collection = get_collection(collection_cid,request)
  
                        if os.path.join(path, name) in atlases:
 
                            new_image = Atlas(name=spaced_name,
                                          description=raw_hdr['descrip'], collection=collection)

                            new_image.label_description_file = ContentFile(
                                        open(atlases[os.path.join(path,name)]).read(),
                                                                    name=name + ".xml")
                        else:
                            new_image = StatisticMap(name=spaced_name, is_valid=False,
                                    description=raw_hdr['descrip'] or label, collection=collection)
                            new_image.map_type = map_type

                        new_image.file = f
                        new_image.save()

                except:
                    error = traceback.format_exc().splitlines()[-1]
                    msg = "An error occurred with this upload: {}".format(error)
                    messages.warning(request, msg)
                    return HttpResponseRedirect(collection.get_absolute_url())
                finally:
                    shutil.rmtree(tmp_directory)
                if not niftiFiles:
                    messages.warning(request, "No NIFTI files (.nii, .nii.gz, .img/.hdr) found in the upload.")
                return HttpResponseRedirect(collection.get_absolute_url())
        else:
            form = UploadFileForm()
        return render_to_response("statmaps/upload_folder.html",
                                  {'form': form},  RequestContext(request))

