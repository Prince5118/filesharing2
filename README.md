# File Upload / Download service  

* Project is entirely built on Python and Django . 
* This Project is used to upload files and share those files as expiraable links.






STEPS TO FOLLOW

1 - Make Sure all requirements are matched, refer to end of this document

2 - Make Sure CronJob is running, To do so
    python schedule.py

3 - python manage.py runserver 10.35.28.189:8000






***********************************
What does each file and folder mean??
***********************************

***********************************
deletingfolders.txt 

is storing output from script.py
It is to make sure everything is running fine
It stores time of each cronjob run and whether any file or SharedRecord is deleted.
***********************************

***********************************
datadump.json

Backup of Data in Sqlite3 database
***********************************

***********************************
linksharing.log

It stores the log for links shared,accessed and of deletion of SharedRecord and Files from SharedFolder
***********************************

***********************************
linksharing.log

It stores the log for links shared,accessed and of deletion of SharedRecord and Files from SharedFolder
***********************************

***********************************
script.py

Its the python script used for CronJob
***********************************

***********************************
malicious.log

Its the logfile for storing malicious attempts on link viewing part
***********************************

***********************************
schedule.py

Its the python script used for initializing the CronJob
***********************************

***********************************
requirements.txt

Its stores all the requirements
run "pip install -r requirements.txt" to install all libraries
***********************************

***********************************
upload folder

It used to store user uploaded files and SharedFolder (named as Private) before implementation of Samba Server
***********************************

***********************************
staticfiles folder

It contains all the jquery css images and Fonts added to templates of this Web-App
***********************************











