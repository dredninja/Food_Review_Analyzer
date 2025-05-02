from django.db import models
from mongoengine import Document, FileField, StringField
import mongoengine

from djongo import models
from mongoengine import Document, StringField
from django import forms

class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())


class UploadedFile(models.Model):
    id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.name

class UserFile(Document):
    file = FileField()  # This field is for storing the file in MongoDB
    name = StringField(max_length=200) 

class User(Document):
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=True, max_length=50)
    username = StringField(required=True, unique=True, max_length=150)
    password = StringField(required=True)