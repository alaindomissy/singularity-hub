from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Hidden
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, TabHolder, Tab
from shub.apps.shub.models import Container, ContainerCollection, Workflow, WorkflowCollection
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from django.forms import ModelForm, Form
from django import forms
from glob import glob
import os


class ContainerForm(ModelForm):

    class Meta:
        model = Container
        fields = ("description","image")

    def clean(self):
        cleaned_data = super(ContainerForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(ContainerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout()
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))


class ContainerCollectionForm(ModelForm):

    class Meta:
        model = ContainerCollection
        fields = ("name","description")

    def clean(self):
        cleaned_data = super(ContainerCollectionForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(ContainerCollectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout()
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))


class WorkflowForm(ModelForm):

    class Meta:
        model = Workflow
        fields = ("name","containers")

    def clean(self):
        cleaned_data = super(WorkflowForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(WorkflowForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout()
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))


class WorkflowCollectionForm(ModelForm):

    class Meta:
        model = WorkflowCollection
        fields = ("name","description")

    def clean(self):
        cleaned_data = super(WorkflowCollectionForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(WorkflowCollectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout()
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))
