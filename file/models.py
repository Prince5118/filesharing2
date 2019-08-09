from django.db import models
from django.contrib.auth.models import User
from datetime import *


from fus.settings import BASE_DIR,PROJECT_ROOT, SHARED_FOLDER

#from file.models import User,File
#all the fields of user
#auth_token, date_joined, email, files, first_name, groups, id, is_active,
# is_staff, is_superuser, last_login, last_name, logentry, password,
#user_permissions, username,who



#########
# Class to represent a file Record in database uploaded by user
#########
class File(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    user = models.ForeignKey(User, related_name = 'files', on_delete=models.CASCADE)
    path = models.CharField(max_length=200)

    def __str__(self):
    	return self.name

    class Meta:
        ordering = ['name']


###########
#Refer to Project Report for Explaination of Models.py
##########
class SharedRecord(models.Model):
    copypath = models.CharField(max_length = 255,default='')
    copyname = models.CharField(max_length = 255,default='')
   
    originalpath = models.CharField(max_length = 255)
    originalname = models.CharField(max_length = 255)
    
    contenthash = models.CharField(max_length=64)   
    pathhash = models.CharField(max_length =  64)
    sender = models.CharField(max_length=255,default = '')
    reciever = models.CharField(max_length = 255)
    ekey = models.CharField(max_length = 255,default='')
    linkidentifier = models.CharField(max_length = 255,default='')   
    linkpassword = models.CharField(max_length=255,default='')
    #evalue = models.CharField(max_length = 32)
        


    viewed = models.BooleanField(default = False)

    linkcount = models.CharField(max_length = 1,default = '0')
   
    shareddate = models.DateTimeField()
    expirylength = models.CharField(max_length = 5)
    # expirylength in minutes
    expirydate = models.DateTimeField()
   
    def __str__(self):
        return str(self.shareddate)

    class Meta:
        ordering = ['-expirydate']
        unique_together = (('linkidentifier',),)



