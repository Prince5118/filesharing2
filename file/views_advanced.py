from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from file.models import File,SharedRecord
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.views.static import serve
import os,hashlib
import shutil,random,string,subprocess
from io import StringIO
import mimetypes

from fus.settings import BASE_DIR,PROJECT_ROOT, SHARED_FOLDER,MEDIA_ROOT

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
import time 

# root/pjlogin/fus BASE_DIR
#/root/pjlogin/fus/Private/ SHARED_FOLDER

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re

import cryptography
from cryptography.fernet import Fernet
import pyAesCrypt
from os import stat, remove
# key = b'1408' # Use one of the methods to get a key (it must be the same when decrypting)



from datetime import datetime as dt
from datetime import *

def uadmin(request):
    return HttpResponse('uadmin')

def filesharing(request):
    return HttpResponse('filesharing')

def userexpiry(request,nameoffile):
    return HttpResponse('userexpiry')

def testing(request,slug):
    return HttpResponse('testing')

def fetch(request):
    return HttpResponse('Fetch')

def specificuser(request,slug):
    return HttpResponse('specificuser')
