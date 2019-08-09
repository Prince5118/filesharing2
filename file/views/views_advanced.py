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

# Libraries imported for sending mail
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
import time 

# Paginator Library
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re

# Couple of Libraies For Encryption
import pyAesCrypt
from os import stat, remove
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

# used for encrypting key
from cryptography.fernet import Fernet
# key = b'1408' # Use one of the methods to get a key (it must be the same when decrypting)



from datetime import datetime as dt
from datetime import *


# Encryption key for encrypting the encryption key and saved in database
adminkey = 'fdkO4373314fFuDJwPzqixmVDXX0p5Tdf5iuoBaD1_U='

# global variables for logfiles and password 
globalvariable = ''
logfile = os.path.join(PROJECT_ROOT,'linksharing.log')
mallogfile = os.path.join(PROJECT_ROOT,'malicious.log')
PASSCODE = 'u123'

# Library for samba connection
import tempfile
from smb.SMBConnection import SMBConnection

# random generator function of given length
def genkey(c):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(c))
    return x

# genhash function returns hash value for given filepath
def genhash(filepath):
    BLOCKSIZE =4096
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return (hasher.hexdigest())

# generates hash function for file object provided
def genhash2(fileobj):
    BLOCKSIZE = 4096
    hasher = hashlib.sha256()
    fileobj.seek(0)

    buf = fileobj.read(BLOCKSIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fileobj.read(BLOCKSIZE)
    return (hasher.hexdigest())


# Writing Log in given logfile
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


# this will be used as a button next to download in home page
def sharefile(request):
    if request.user.is_authenticated:
                if request.method=='POST':
                   
                    user = User.objects.get(username=request.user.username)
                        # user is representing the sending user
                    files = user.files.all()
                #       users will represent all the available users he can send to ,so we can delete the name of sender from that list
                    users = [str(u) for u in User.objects.all()]
                    try:
                
                        selected_file = File.objects.filter(user=User.objects.get(username=request.user.username),name=request.POST['filename'])
                        print(selected_file)
                    except(KeyError):
                        return render(request,'file/home.html',{'error_message':"You DID NOT SELECT A FILE",})
                    else:
                        t = str(selected_file[0])
              

                        # removes sender from the list
                        users = [str(u) for u in users if u != str(user)]
                        choices = ['1','10','30','60','1440']
     
     
                        return render(request,'file/sharefile.html',{  
                        'nameoffile':t,
                        'sender':user,
                        'users':users,
                        'choicelist':choices,
                        })

                else :
                   # return render(request,'file/home.html',{'error_message':"You DID NOT SELECT A FILE method used was get",})
                     return render(request,'file/error_share.html')

    else:
        return redirect('file:login')


# view function adding reciever and expiry for a particular file
def userexpiry(request,nameoffile):
    if request.user.is_authenticated:
                if request.method=='POST':
                    bufferSize = 64 * 1024
                    global logfile
                    # list of recievers names
                    list_of_recievers = request.POST.getlist('recievers')

                    #expiry in minutes they selected
                    expiryminutes = request.POST.get('expirychoice')

                    #sender object
                    user = User.objects.get(username=request.user.username)

                    #selected file object
                    files = user.files.all()
                    selected_file = user.files.get(name=nameoffile)

                    # tells us original path and name of file
                    filepath = selected_file.path
                 
                    display = ''
                   
                    
                    # Cant Share File greater then 250 mb
                    maxsize = 50144000
                    statinfo = os.stat(filepath) 
             
                    if int(statinfo.st_size)>maxsize:
                        return HttpResponse('You Cant Share File of size greater than 250 MegaBytes')
             
                    # Establishing samba connection for uploading file to sharedfolder after encryption 
                    global PASSCODE
                    client_machine_name= 'megh-os-101317.megh.barc.gov.in'
                    server_name =  'megh-os-101317.megh.barc.gov.in'
                    userID = request.session['username']
                    password = PASSCODE
                    conn = SMBConnection(userID, password, client_machine_name, server_name, use_ntlm_v2 = True)
                    server_ip = '10.35.28.189'
                    assert conn.connect(server_ip, 139)
                    # Connection done                    

                    # reading file to be encrypted in a file object
                    file_obj = tempfile.NamedTemporaryFile()
                    conn.retrieveFile('homes','/'+selected_file.name, file_obj)
                    file_obj.seek(0)
                    data = file_obj.read()
                    conn.close()
                    #hash1 is hash value for file saved in user folder
                    hash1 = str(genhash2(file_obj))
                    file_obj.close()
                    hash2 = str(hashlib.sha256(filepath.encode()).hexdigest())
                    # Checking if the file shared already exists in SharedFOlder or not
                    # if it does then compare hash value to check if file in user folder has been tampered or not
                                     


                    flag = 0
                    sharedobj = SharedRecord.objects.filter(originalpath = filepath)
                    
                    for i in sharedobj:
                        if i.contenthash == hash1 and i.pathhash == hash2:
                            dst = i.copypath
                            print('here')
                            examplecopyname = i.copyname
                            keytobeused  = i.ekey
                            flag = 1
                            break
                       
                    #content changed of shared file compared to previous share
                   
                    # Updating immediately
                    #ext = nameoffile.split('.',1)[1]
                    src = filepath
         
                   
                    # Flag=0 means that file has not been shared before and is not saved in sharedfolder currently
                    if flag==0:
                                           
                        s = datetime.now()
                       
                        #salt = get_random_bytes(32) # Salt you generated
                        #password = b'password123' # Password provided by the user, can use input() to get this
                        #keytobeused = PBKDF2(password, salt, dkLen=32) # Your key that you can encrypt with
                        keytobeused = genkey(32)
                        keytobeused = keytobeused.encode()
                        
                        # examplecopyname is random string link
                        examplecopyname = str(genkey(32))
                        #dst is path where file is saved in sharedfolder
                        dst = '/home/sharedfolder/'+ examplecopyname

 
                        
                        # Create cipher object and encrypt the data
                        cipher = AES.new(keytobeused, AES.MODE_CBC) # Create a AES cipher object with the key using the mode CBC
                        ciphered_data = cipher.encrypt(pad(data, AES.block_size)) # Pad the input data and then encrypt
                                             
                        # Establishing Samba server connection for saving encrypted file in sharedfolder                       
                        conn = SMBConnection(userID,password, client_machine_name, server_name, use_ntlm_v2 = True)
                        assert conn.connect(server_ip, 139)
                        
                        # storing encrypted content in file object
                        file_share = tempfile.NamedTemporaryFile()
                        file_share.seek(0)
                        file_share.write(cipher.iv)
                        file_share.write(ciphered_data)
                        file_share.seek(0)
                        
                        # saving file object in samba server with tempvar as intended filename and file_share as its content
                        tempvar = '/'+examplecopyname
                        conn.storeFile('sharedfiles',tempvar,file_share)
                        conn.close()
                        e = datetime.now()
                        t = e - s
                        print('Encryption- ' + str(t))
              
                        #######
                    # Encrypting the encryption key and saving it in storekey variable
                    global adminkey
                    f = Fernet(adminkey)
                    keytobeused = keytobeused.encode()
                    storekey = f.encrypt(keytobeused)
                        
                    print(storekey)



                        # Creating SharedRecord for each reciever in database and writing them in logfile including displaying output in screen 
                    for item in list_of_recievers:
                        # Getting userrecord id for sender and reciever
                        temp = str(item)
                        # this variable contains expiry date of link
                        whentogo = datetime.now()+timedelta(minutes = int(expiryminutes))
                           
                        # object created as SharedRecord to be used in Sharing of File
                       
                        nameoflink = genkey(32)

                        obj = SharedRecord(originalpath=filepath,
                            copypath = dst,copyname =examplecopyname,
                            originalname=os.path.basename(filepath),shareddate=datetime.now(),
                            expirylength = expiryminutes,expirydate = whentogo,
                            contenthash = str(genhash(filepath)),pathhash = hashlib.sha256(filepath.encode()).hexdigest(),
                            sender = user.username,reciever = temp,
                            ekey = storekey,linkidentifier = nameoflink,linkpassword=genkey(8),
                            )
                        # obj.save() This line cut to last such that model is saved only after copying
                        obj.save()
                        
                        # Writing the share record in logfile
                        logtext = str(obj.shareddate.replace(microsecond=0))+' '+obj.sender+' Shared '+ obj.originalname  +' with '+obj.reciever        
                        write_log(logtext,logfile)
                       # display variable is what output you get in screen at the end of sharing containing linkname username and link-password
                        display = display +'<a href="http://10.35.28.189:8000/'+ obj.linkidentifier+'"  target="_blank"  >'+'http://10.35.28.189:8000/'+obj.linkidentifier +'</a>'+"<br>" + temp + "<br>"+ obj.linkpassword +"<br><br>"
    
                    

                    ###################
                    # email part should come here
                    #send_mail('<Your subject>', '<Your message>', 'from@example.com', ['wanisachin3@gmail.com'])
                    """
                    message = display
                    subject = 'Testing'
                    #from_email = settings.DEFAULT_FROM_EMAIL
                    from_email = 'LinkSharing'
                    to_email = ['wanisachin3@gmail.com']

                    send_mail(subject,message,from_email,to_email,fail_silently=False)
                    """
                    #################
                    return HttpResponse(display)

                else :
                    #request.method='GET'
                    # return render(request,'file/home.html',{'error_message':"You DID NOT SELECT A FILE method used was get",})
                     return render(request,'file/error_share.html')

    else:
        return redirect('file:login')


# testing view is used when user reciever clicks on link he got, slug is the part which is link-identifier 
def testing(request,slug):    
    temp = SharedRecord.objects.filter(linkidentifier = str(slug))
    #x = temp[0]

    #Checkng if valid link
    if not temp:
        return HttpResponse('Invalid Link')

    #if viewed already
    x = temp[0]

    # if expiration date passed
    currentdate = datetime.now()
    isexpired = 0   
    viewed = 0

    if x.expirydate<currentdate:
        isexpired = 1
    if x.viewed==True:
        viewed = 1


    # passing everydata in context like link expired viewed or not
    context = {'nameoflink':x.linkidentifier,'sharedobject':x,'linkcount':int(x.linkcount),
                'viewed':viewed,'isexpired':isexpired,'wrong':0}
    return render(request, 'file/Login_v1/askuser.html', context)


# checks username and password enetered in link when link is not viewed and expired
def filesharing(request):
    
    if request.method=='POST':
        
        global logfile
        global mallogfile
        
        requesting_user = request.POST['username']
        # removing spaces from the end of userID entered 
        requesting_user = requesting_user.replace(" ", "")
    
        var = request.POST['nameoflink']
        # The password entered by user in link
        entered_password = request.POST['hashedkey']
    
        temp = SharedRecord.objects.filter(linkidentifier = var)
        x = temp[0]

        #Autheticating the entered credentials
        wrong = 0

       # Checking if enetered credentials are correct or not 
        if requesting_user.lower()!=x.reciever or entered_password!=x.linkpassword:
            # return to some error page saying you are not autheticated user
            # maybe increase authentication count like user tried 5 times or something
            wrong_attempt_datetime = datetime.now().replace(microsecond=0)
            #wrong_attempt_datetime += timedelta(hours=5)+timedelta(minutes=30)
            bufferSize = 64 * 1024
           
            # intcount maintains how many times wrong credentials have been entered for the link 
            intcount = int(x.linkcount)
            intcount = intcount + 1
            x.linkcount = str(intcount)
            x.save()
            wrong = 1
           # context having all the data required for html page like is entered credentiasl wrong or not 
            context = {'nameoflink':x.linkidentifier,'sharedobject':x,'linkcount':int(x.linkcount),
                'viewed':int(x.viewed),'isexpired':0,'wrong':wrong}
            
            #malicious attempt and creating its log
            whyrejected = ''
            if requesting_user.lower()!=x.reciever and entered_password!=x.linkpassword:
                whyrejected = 'WrongID-Password'
            elif requesting_user.lower()!=x.reciever:
                whyrejected = 'WrongID'
            else :
                whyrejected = 'WrongPassword'
            # date time linkname sender filename intendedreciever attemptedby whyrejected wrongattemptcount
            logcontent = str(wrong_attempt_datetime)+ ' '+x.linkidentifier+' '+ x.sender + ' '+ x.originalname+' '+x.reciever+' '+requesting_user+' '+whyrejected+' '+x.linkcount
            write_log(logcontent,mallogfile)

            return render(request, 'file/Login_v1/askuser.html', context)



        # if expiration date passed
        currentdate = datetime.now()
        if x.expirydate<currentdate:
            return HttpResponse('Link Expired')  
        
        # accessing individual attributes of ShardRecord object of that link
        # what was link sender , intended reciever etc.. 
        linkidentifier = x.linkidentifier
        copyname = x.copyname
        copypath = x.copypath
        originalname = x.originalname
        sender = x.sender 
        reciever = x.reciever
     
        # helps in identifying the file type extension
        typeofmime = str(mimetypes.MimeTypes().guess_type(originalname)[0])
        
        # the encrypted encryption key
        key = x.ekey

        ###########
        #Decryption and logging 

 

        start = datetime.now()
        
        # Establishing Samba Connection for downloading file from sharedfolder after proper decryption
        global PASSCODE
        userID = request.session['username']
        client_machine_name= 'megh-os-101317.megh.barc.gov.in'
        server_name =  'megh-os-101317.megh.barc.gov.in'
        conn = SMBConnection(userID,PASSCODE , client_machine_name, server_name, use_ntlm_v2 = True)
                  
        server_ip = '10.35.28.189'
        assert conn.connect(server_ip, 139)
        # connection established

        # storing content of file in sharedfolder to fileobj
        file_obj = tempfile.NamedTemporaryFile()
        file_obj.seek(0)
        tempvar = '/'+copyname
        conn.retrieveFile('sharedfiles',tempvar, file_obj)

        # reading iv and cipher text from file_obj
        file_obj.seek(0)
        iv = file_obj.read(16)
       
        ciphered_data = file_obj.read()
        file_obj.seek(0)

        # decoding the encryption key from adminkey using Cryptography library of python
        key = key.encode()       
        global adminkey
        f = Fernet(adminkey)
        key = f.decrypt(key)

        # Decrypting the content on the fly 
        key = key.encode()
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)  # Setup cipher
        encrypted = unpad(cipher.decrypt(ciphered_data), AES.block_size) # Decrypt and then up-pad the result
     
 
        end = datetime.now()
        timetaken = end-start
        timetaken = str(timetaken)
        print('Time Decryption: '+timetaken) 

        # Creating file access log in linksharing logs
        logtext = str(datetime.now().replace(microsecond=0))+' '+reciever + ' accessed ' + originalname + ' sharedby '+sender

        write_log(logtext,logfile) 


        # Returning the decrypted content to be downloaded by reciever and updating databsse
        response = HttpResponse(encrypted)
        response['Content-Type'] = typeofmime
        response['Content-Disposition'] = 'attachment; filename= "{}"'.format(originalname)
        x.viewed=True
        x.save()
        return response

        return HttpResponseRedirect('') 
    
    else:
        return HttpResponse("Unsupported method Please use GET or POST ", status=405)

# Function for admin home page

# this view was used when admin logs in
# this displays the malicious logs , linksharing logs and passes the content to be displayed after reading from logfiles and passes content to html page
def uadmin(request):
    if request.user.is_authenticated and request.method == 'GET' and request.user.username=='admin':
        global logfile
        global mallogfile

        # Reading from logfile 
        with open(logfile, 'r') as f:
            lines = [line.rstrip('\n').split(' ') for line in f]
        
        # Displayingonly latest 1000 log inputs , this could be changed depending upon requirement
        lines = lines[:1000]
        
        # Pagination Implementation
        page = request.GET.get('page', 1)

        paginator = Paginator(lines, 30)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
             
            #2019-06-21 12:43:22.363334 user1 Shared user1_readme.txt with admin
            #2019-06-21 12:44:55.697242 admin accessed user1_readme.txt sharedby user1
        
        # Reading from malicious log
        with open(mallogfile,'r') as f:
            lines = [line.rstrip('\n').split(' ') for line in f]
             
        
        # malicious log pagination
        page = request.GET.get('page', 1)
         
        paginator = Paginator(lines, 9)
        try:
            malicious_data = paginator.page(page)
        except PageNotAnInteger:
            malicious_data = paginator.page(1)
        except EmptyPage:
            malicious_data = paginator.page(paginator.num_pages)

        #listofuser 
        countofuser = User.objects.all().count()
        alluser = User.objects.all()
        listofuser = [str(item) for item in alluser]

        context = {'data':data,'malicious_data':malicious_data,'listofuser':listofuser,'countofuser':countofuser}

        return render(request, 'file/uadmin.html', context)

    else:
        return HttpResponse('Wrong')

# fetches from search box of admin and passes them to specificuer view
def fetch(request):
    if request.user.is_authenticated  and request.user.username=='admin' :
        if request.method=="POST":
            x = request.POST['nameofuser']
            var = '/uadmin/view='+str(x)
            return HttpResponseRedirect(var)
        else:
            return HttpResponse("Unsupported method Please use GET or POST ", status=405)
    else:
        return HttpResponseRedirect('')




# Specific User Search Request
def specificuser(request,slug):
    if request.user.is_authenticated  and request.user.username=='admin' :
        x = slug
        global logfile
        global mallogfile 
        listofrecord = []
     
        # searches for slug keyword in logfile and stores them in list
        with open(logfile, 'r') as f:
            for line in f:
                if re.search(x, line):
                    line = line[:-1]# remving /n character
                    line = line.split(' ')
                    listofrecord.append(line)

        

        # pagination
        page = request.GET.get('page', 1)

        paginator = Paginator(listofrecord, 15)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)


        return render(request, 'file/specificuser.html', {'data':data})

    #2019-06-21 12:43:22.363334 user1 Shared user1_readme.txt with admin
    #2019-06-21 12:44:55.697242 admin accessed user1_readme.txt sharedby user1
    # username is 2nd and 6th index

    else:
        return HttpResponseRedirect('')



