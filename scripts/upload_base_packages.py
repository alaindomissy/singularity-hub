# upload_base_packages.py will generate an initial collection and upload the base packages
# under shub/apps/shub/data/packages to it. We will then read in data structures for these base
# images, and save them to be used for later comparison

from shub.apps.shub.models import ContainerCollection
from shub.apps.shub.utils import save_package
from singularity.package import load_package
from django.contrib.auth.models import User
from glob import glob
import pandas
import numpy
import os

here = os.path.dirname(os.path.realpath(__file__))
package_dir = os.path.abspath(os.path.join(here,"..","shub","apps","shub","data","packages"))
base_packages = glob("%s/*.zip" %(package_dir))

# Here we will save a list of features (paths in rows) by base images (columns)

# Upload each package, first save common features (folder paths) to list
folders = []
for base_package in base_packages:
    print("Adding package %s to folders features..." %(os.path.basename(base_package)))
    package = load_package(base_package,get=['folders.txt'])        
    folders = numpy.unique(folders + package['folders.txt']).tolist()

features = pandas.DataFrame(0,index=folders,columns=base_packages)
for base_package in base_packages:
    print("Parsing features from %s..." %(os.path.basename(base_package)))
    package = load_package(base_package,get=['folders.txt'])        
    features.loc[package["folders.txt"],base_package] = 1

# Save features to csv, pickle, etc.
features.to_csv("%s/folder_features.tsv" %package_dir,sep="\t")
features.to_pickle("%s/folder_features.pkl" %package_dir)

# Create a superuser (this will need to be different in production)
admin = User.objects.create_superuser(username='shub', password='shub', email='')

# Now let's create a collection with the base images
collection = ContainerCollection()
collection.name = "Singularity Base Images"
collection.description = "a small collection of base images for comparing newly imported images to."
collection.owner = admin
collection.save()

# Upload each package to that collection
for base_package in base_packages:
    new_container = save_package(collection,base_package)
