from singularity.package import get_image_hash, load_package, list_package
from django.core.files.uploadedfile import UploadedFile
from shub.apps.shub.models import Container
from shub.settings import MEDIA_ROOT
import shutil
import os
import re

def save_image_upload(collection,image,container=None):
    '''save_image_upload will save an image object to a collection
    :param collection: the collection object
    :param container: the container object, e.g., if updating
    '''
    if container==None:
        container = Container(collection=collection)
    collection_dir = "%s/%s" %(MEDIA_ROOT,collection.id)
    if not os.path.exists(collection_dir):
        os.mkdir(collection_dir)
    container_file = '%s/%s' %(collection_dir,image.name)
    with open(container_file, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    container.name = image.name
    container.version = get_image_hash(container_file)
    container.image = image
    container.image.name = image.name
    container.save()
    return container


def save_package(collection,package,container=None):
    '''save_package_upload will save a package object to a collection
    by way of extracting the image to a temporary location, and
    adding meta data to the container
    :param collection: the collection object
    :param package: the full path to the package
    :param container: the container object, e.g., if updating
    '''
    if container==None:
        container = Container(collection=collection)
    collection_dir = "%s/%s" %(MEDIA_ROOT,collection.id)
    if not os.path.exists(collection_dir):
        os.mkdir(collection_dir)
    # Unzip the package image to a temporary directory
    includes = list_package(package)
    image_path = [x for x in includes if re.search(".img$",x)]
    # Only continue if an image is found in the package
    if len(image_path) > 0:
        image_path = image_path[0]
        contents = load_package(package)
        # Move the file to it's final location
        container_file = contents[image_path]
        container.name = image_path
        container.version = get_image_hash(container_file)
        container.image.save(image_path,File(open(container_file, 'r')))
        container.save()
        # Add the container to the collection
        collection.container_set.add(container)
        collection.save
        # Clean up temporary directory
        shutil.rmtree(os.path.dirname(container_file))
        return container
    return None

