from shub.apps.shub.models import Container
from shub.settings import MEDIA_ROOT
from django.core.files import File
import shutil
import os

def save_image_upload(collection,image,container=None):
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
    container.image = image
    container.image.name = image.name
    container.save()
    return container
