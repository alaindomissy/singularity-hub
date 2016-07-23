from guardian.shortcuts import assign_perm, get_users_with_perms, remove_perm
from django.db.models.signals import m2m_changed
from shub.apps.shub.storage import ImageStorage
from polymorphic.models import PolymorphicModel
from django.core.urlresolvers import reverse
from taggit.managers import TaggableManager
from django.contrib.auth.models import User
from django.db.models import Q, DO_NOTHING
from shub.settings import MEDIA_ROOT
from jsonfield import JSONField
from django.db import models
import collections
import operator
import os

#######################################################################################################
# Supporting Functions and Variables ##################################################################
#######################################################################################################

def get_upload_folder(instance,filename):
    '''get_upload_folder will return the folder for an image associated with the ImageSet id.
    instance: the Image instance to upload to the ImageCollection
    filename: the filename of the image
    '''
    collection_id = instance.collection.id
    # This is relative to MEDIA_ROOT
    return os.path.join('images',str(collection_id), filename)


PRIVACY_CHOICES = ((False, 'Public (The collection will be accessible by anyone and all the data in it will be distributed under CC0 license)'),
                   (True, 'Private (The collection will be not listed. It will be possible to share it with others at a private URL.)'))


#######################################################################################################
# Containers ##########################################################################################
#######################################################################################################

class ContainerCollection(models.Model):
    '''A container collection is a grouping of containers owned by one or more users
    '''

    # Container Collection Descriptors
    name = models.CharField(max_length=200, null=False, verbose_name="Name of collection")
    description = models.TextField(blank=True, null=True)
    add_date = models.DateTimeField('date published', auto_now_add=True)
    modify_date = models.DateTimeField('date modified', auto_now=True)
    # not sure if we will need these with version control

    # Users
    owner = models.ForeignKey(User)
    contributors = models.ManyToManyField(User,related_name="container_collection_contributors",related_query_name="contributor", blank=True,help_text="Select other singularity hub users to add as contributes to the collection.",verbose_name="Contributors")

    # Privacy
    private = models.BooleanField(choices=PRIVACY_CHOICES, default=False,verbose_name="Accesibility")
    private_token = models.CharField(max_length=8,blank=True,null=True,
                                     unique=True,db_index=True, default=None)

    def get_absolute_url(self):
        return_cid = self.id
        return reverse('container_collection_details', args=[str(return_cid)])

    def __unicode__(self):
        return self.name

    def get_label(self):
        return "container_collection"

    def save(self, *args, **kwargs):
        super(ContainerCollection, self).save(*args, **kwargs)
        assign_perm('del_container_collection', self.owner, self)
        assign_perm('edit_container_collection', self.owner, self)

    class Meta:
        ordering = ["name"]
        app_label = 'shub'
        permissions = (
            ('del_container_collection', 'Delete container collection'),
            ('edit_container_collection', 'Edit container collection')
        )

class Container(models.Model):
    '''A container is a (singularity) container, stored as a file (image) with a unique id and name
    The user can specify the description, but the name comes from the file
    '''
    name = models.CharField(max_length=250, null=False, blank=False)
    description = models.CharField(max_length=1000, null=True, blank=True)
    image = models.FileField(upload_to=get_upload_folder,null=True,blank=False)
    collection = models.ForeignKey(ContainerCollection,null=False,blank=False)
    tags = TaggableManager()

    # Will need to add version control to Container model here

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_label(self):
        return "container"

    class Meta:
        ordering = ['name']
        app_label = 'shub'

    # Get the url for a container
    def get_absolute_url(self):
        return_cid = self.id
        return reverse('container_details', args=[str(return_cid)])


#######################################################################################################
# Workflows ###########################################################################################
#######################################################################################################

class WorkflowCollection(models.Model):
    '''A workflow collection is a grouping of workflows owned by one or more users
    '''

    # Workflow Collection Descriptors
    name = models.CharField(max_length=200, null=False, verbose_name="Name of workflow collection")
    description = models.TextField(blank=True, null=True)
    add_date = models.DateTimeField('date published', auto_now_add=True)
    modify_date = models.DateTimeField('date modified', auto_now=True)

    # Users
    owner = models.ForeignKey(User)
    contributors = models.ManyToManyField(User,related_name="workflow_collection_contributors",related_query_name="contributor", blank=True,help_text="Select other singularity hub users to add as contributers to the collection.",verbose_name="Contributors")

    # Privacy
    private = models.BooleanField(choices=PRIVACY_CHOICES, default=False,verbose_name="Accesibility")
    private_token = models.CharField(max_length=8,blank=True,null=True,
                                     unique=True,db_index=True, default=None)

    def get_absolute_url(self):
        return_cid = self.id
        return reverse('workflow_collection_details', args=[str(return_cid)])

    def get_label(self):
        return "workflow_collection"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(WorkflowCollection, self).save(*args, **kwargs)
        assign_perm('del_workflow_collection', self.owner, self)
        assign_perm('edit_workflow_collection', self.owner, self)

    class Meta:
        ordering = ["name"]
        app_label = 'shub'
        permissions = (
            ('del_workflow_collection', 'Delete workflow collection'),
            ('edit_workflow_collection', 'Edit workflow collection')
        )


class Workflow(models.Model):
    '''A workflow is a wdl specification that includes a set of containers
    '''
    name = models.CharField(max_length=1000, null=False, blank=False)
    collection = models.ForeignKey(WorkflowCollection,null=False,blank=False)
    wdl = models.CharField(max_length=1000, null=False, blank=False)
    
    # Containers - usage is specified in wdl, and list of current containers maintained here
    containers = models.ManyToManyField(Container,related_name="collection_workflows",related_query_name="collection_workflows", blank=True,help_text="Containers associated with the workflow.",verbose_name="Containers in a workflow")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_label(self):
        return "workflow"

    class Meta:
        ordering = ['name']
        app_label = 'shub'

    # Get the url for a container
    def get_absolute_url(self):
        return_cid = self.id
        return reverse('workflow_details', args=[str(return_cid)])


def contributors_changed(sender, instance, action, **kwargs):
    if action in ["post_remove", "post_add", "post_clear"]:
        current_contributors = set([user.pk for user in get_users_with_perms(instance)])
        new_contributors = set([user.pk for user in [instance.owner, ] + list(instance.contributors.all())])

        for contributor in list(new_contributors - current_contributors):
            contributor = User.objects.get(pk=contributor)
            assign_perm('edit_%s' %(sender.get_label()), contributor, instance)

        for contributor in (current_contributors - new_contributors):
            contributor = User.objects.get(pk=contributor)
            remove_perm('edit_%s' %(sender.get_label()), contributor, instance)

m2m_changed.connect(contributors_changed, sender=ContainerCollection.contributors.through)
m2m_changed.connect(contributors_changed, sender=WorkflowCollection.contributors.through)
