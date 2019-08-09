#!/usr/bin/python

#Used for connecting to Samba Server
from smb.SMBConnection import SMBConnection

import shutil
from os import listdir
from os.path import isfile, join

#Django Setup to read database
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fus.settings")
django.setup()


from crontab import CronTab

#Reading from database after connection to django
from file.models import User,SharedRecord,File

# Reading Project Directory Media root from settings file
from fus.settings import BASE_DIR,PROJECT_ROOT, SHARED_FOLDER,MEDIA_ROOT

from datetime import datetime



##################
### Connection to Samba server, UserID and password are used of Admin

client_machine_name= 'megh-os-101317.megh.barc.gov.in'
server_name =  'megh-os-101317.megh.barc.gov.in'
userID = 'admin'
password = 'u123'


conn = SMBConnection(userID, password, client_machine_name, server_name, use_ntlm_v2 = True)
server_ip = '10.35.28.189'
assert conn.connect(server_ip, 139)
################

#Function to write logs of file adn SharedRecord deletion in LinkSharing Log
def write_log(text, logfile):
        #We read the existing text from file in READ mode
    f=open(logfile,"r")
    fline=text + "\n"    #Prepending string
    oline=f.readlines()
    #Here, we prepend the string we want to on first line
    oline.insert(0,fline)
    f.close()


    #We again open the file in WRITE mode
    src=open(logfile,"w")
    src.writelines(oline)
    src.close()
    return

# Variable to store all SharedRecord as List
temp = SharedRecord.objects.all()


# Getting List of All files in SharedFolder which are not Hidden
flist  = conn.listPath('sharedfiles', '')
flist = [item.filename for item in flist]
flist = [item for item in flist if not item.startswith('.')]



#deleting Shared Records
now = datetime.now()
print(str(now))


logfile = os.path.join(PROJECT_ROOT,'linksharing.log')

# For Loop to check each SharedRecord and Delete them if expired from Database

for item in temp:
    if item.expirydate<datetime.now():

        # Writing them in Log File and amking sure Date is written in log file in appropriate format
        print('deleting a sharedrecord')
        now = datetime.now()
        now = now.replace(microsecond=0)
        text1 = ''
        now = str(now)
        text1 += now+' '+item.sender+' Deleted_SharedRecord '+item.originalname +' '+str(item.shareddate.date())+'_'+str(item.shareddate.time().replace(microsecond=0))+' '+item.reciever
        write_log(text1,logfile)

        # Actually Deleting SharedRecord
        item.delete()


#deleting files
for item in flist:

    flag = 0

    # flag 0 means its currently not used in any sharedrecord
    for record in temp:
        if record.copyname==str(item):
            flag=1
            # d = SHARED_FOLDER + item

    # If flag gets 0 means that file in SharedFolder is not linked to any SHaredRecord in database and must be deleted from server
    if flag==0:

        print(item)
        # Deleting File from SharedFolder
        # 'sharedfiles' is name of Share which is written in smb.conf file
        conn.deleteFiles('sharedfiles','/'+item)


        # Writing Log for delete file
        text = str(now.replace(microsecond=0))+' '+'System'+' Deleted_File '+item+' '+'-'+' '+'-'
        write_log(text,logfile)

# Closing the Samba Connection
conn.close()

