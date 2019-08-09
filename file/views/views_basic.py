from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from file.models import File,SharedRecord
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.views.static import serve
import os


from fus.settings import BASE_DIR,PROJECT_ROOT, SHARED_FOLDER
# root/pjlogin/fus BASE_DIR
#/root/pjlogin/fus/SharedFolder/ SHARED_FOLDER

#########
import os,hashlib
import shutil,random,string,subprocess
from io import StringIO
import mimetypes
##########


"""
Mapping of username and password to django users for samba

UserName Account_Password Samba_Password

u1 User11999* u123
u2 User21999* u123
u3 User31999* u123
admin Prince1999* u123

users: u1 u2 u3 admin
Password for Samba

"""
PASSCODE = 'u123'

"""
2 Important Libraries ued for reading files and writing them back in a samba server
"""
import tempfile
from smb.SMBConnection import SMBConnection


# Function to generate random strings on length c
def genkey(c):
    x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(c))
    return x


## home view displaying users files and providing him with options to download upload and share
def home(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        files = user.files.all()

        # Paginator to display max 5 files ata time and then creating a paginator object
        paginator = Paginator(files, 5)
        page = request.GET.get('page',1)

        # Variable to check if User is admin or not
        # It was supposed to be used for adding a button specifically on admin home page to go to LinkSharing and Malicious Log page
        # This Feature was not implemented
        val = 0
        print(user)
        if user=='admin':
            val = 1
        
        # trying to paginate files, throws exception if page number enetered to be viewed is not a integer -- This could be done by manipulating the url in search engine
        if bool(files):
            files = paginator.page(page)
            try:
                files = paginator.page(page)
            except PageNotAnInteger:
                files = paginator.page(1)
            except EmptyPage:
                files = paginator.page(paginator.num_pages)
            context = {'paginator': paginator,
                       'files': files,
                       'user': user,
                       'admin':val,
                      }
            return render(request, 'file/home.html', context, status=200)
        else:
            context = {'warn_msg': '''You haven't Uploaded any
                                Files just upload some files to access it''',
                        }
            return render(request, 'file/home.html', context, status=200)
    else:
        # trying to access home page without loggin in
        return  redirect('file:login')



# Function that takes userID and password and checks if they are correct
# It also redirect admin login from home page to admin's special login page
def log_in(request):
   
    # User already authenticated but still trying to login redirects him to home page
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    else:

        # Displaying Login Page
        if request.method == 'GET':
            form = AuthenticationForm()
            return render(request, 'file/Login_v1/index.html', {'form': form}, status=200)

        # Checks the enetered credentials in login page
        elif request.method == 'POST':
            #form = AuthenticationForm(data=request.POST)
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                #return HttpResponseRedirect("/")
               # request.session['member_id'] = user.id
                x = form.get_user()
                t = str(x)
 

                # Updates Data in request object
                request.session['member_id'] = x.id
                request.session['username'] = x.username
                request.session['password'] = request.POST['password']
                
                # IF user is admin
                if t=='admin':
                    return HttpResponseRedirect("/uadmin")
                # If user is not admin
                else:
                    return HttpResponseRedirect("/")

            else:
                return render(request, 'file/Login_v1/index.html', {'form': form}, status=200)
        else:
            return HttpResponse("Unsupported method Please use GET or POST ", status=405)



# View Function which comes in play when we select a file to be uploaded
def upload(request):
    if request.user.is_authenticated:
        
        # User is authenticated and is selecting a file
        if request.method == 'GET':
            return render(request, 'file/upload.html', status=200)

        # This Part takes acre of uploading of file by passing request.Files object
        if request.method == 'POST':
            # Try to upload a file
            try:
                file_name, file_path = handle_uploaded_file(request, request.FILES['file'], str(request.FILES['file']))
                # Creating A file Record for user uploaded file in Database
                filevar = File(name=file_name, user=request.user, path=file_path)
                filevar.save()
                # ReDirect to home page after uploading 
                return HttpResponseRedirect("/")
            except KeyError:
                return HttpResponseRedirect("/upload")
            except ValueError:
                return HttpResponse("File Already Exists", status=400)
        else:
            return HttpResponse("Unsupported method Please use GET or POST ", status=405)
    else:
       # User is not logged but is trying to access upload url
        return HttpResponseRedirect("/login")



# Previous Function was more about creating record but selected file is uploaded in chunks using this function
def handle_uploaded_file(request, file, filename):
    global PASSCODE
    user_name = request.user.username
    
    filename = str(filename)

    ## Creating A samba connection for file to be uploaded to samba server    
    client_machine_name= 'megh-os-101317.megh.barc.gov.in'
    server_name =  'megh-os-101317.megh.barc.gov.in'
    userID = request.session['username']
    password = PASSCODE
    
    conn = SMBConnection(userID, password, client_machine_name, server_name, use_ntlm_v2 = True)
    server_ip = '10.35.28.189'
    assert conn.connect(server_ip, 139)
    # Connection Established

    # file obj in which content will be read in chunks 
    file_obj = tempfile.NamedTemporaryFile()
    
    for chunk in file.chunks():
        file_obj.write(chunk)
    file_obj.seek(0)
    
    # path to store that file in user area
    storingpath = '/'+filename
    # Actually storing file
    conn.storeFile('homes',storingpath,file_obj)
    
    file_obj.close()
    # Closing the connection
    conn.close()
    #abs_path = os.path.abspath(path)
    # abs path example - /home/u1/file.txt for 'file.txt' to be uploaded
    # This is useful in creating file record in database to know where files are actually in Samba Server
    abs_path = '/home/'+userID+'/'+filename
    print(abs_path)
    return filename, abs_path


# Django singup to create a new user but this also inputs user email ad updates them in database
def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'file/signup.html', {'form': form}, status=200)
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        emailid = request.POST['emailid']

        if not form.is_valid():
            return render(request, 'file/signup.html', {'form': form}, status=200)
        form.save()
        user = User.objects.get(username=form.cleaned_data.get('username'))
        user.email = emailid
        user.save()
        login(request, user)
        return HttpResponseRedirect("/login")
    else:
        return HttpResponse("Unsupported method Please use GET or POST ", status=405)


# Django Logout
def log_out(request):
    if request.method=='GET':
        logout(request)
        return HttpResponseRedirect("/login")
    else :
        return HttpResponse("Unsupported method Please use GET or POST ", status=405)


# View function to download a file with Samba Server Connection using appropriate mime type
def download(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        files = user.files.all()

        try:
            selected_file = user.files.filter(name=request.POST['filename'])


        except(KeyError):
            render(request,'file/home.html',{'error_message':"You DID NOT SELECT A FILE",})

        else:
            # File object to be selected for downloading purpose
            t = selected_file[0]
            # Finding Appropriate mime type
            typeofmime = str(mimetypes.MimeTypes().guess_type('t.name')[0])
            
            
            #####
            # Setting up samba server connection to read file content to be downloaded by user
            global PASSCODE
            client_machine_name= 'megh-os-101317.megh.barc.gov.in'
            server_name =  'megh-os-101317.megh.barc.gov.in'
            userID = request.session['username']
            password = PASSCODE
        
            conn = SMBConnection(userID, password, client_machine_name, server_name, use_ntlm_v2 = True)
            server_ip = '10.35.28.189'
            assert conn.connect(server_ip, 139)
            # Connection Setup

            # temporary file object in which content would be read
            file_obj = tempfile.NamedTemporaryFile()
            path = '/'+ t.name
            conn.retrieveFile('homes', path, file_obj)
            
            file_obj.seek(0)
            
            # reading from fileobj to a variable
            p = file_obj.read()
            ######
            
            # Content to be downloaded with appropriate mime type extension
            response = HttpResponse(p)
            response['Content-Type'] = typeofmime
            response['Content-Disposition'] = 'attachment; filename= "{}"'.format(t.name)
            return response




