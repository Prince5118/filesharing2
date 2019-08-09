from django.conf.urls import url
import views

app_name = 'file'

urlpatterns = [
    
    # Home Page
    url(r'^$', views.home, name='home'),

    # Admin Home Page
    url(r'^uadmin$',views.uadmin,name='uadmin'),

    #Sharing of File
    url(r'^sharefile',views.sharefile,name='sharefile'),

    # to download a file
    url(r'^download$',views.download,name='download'),

    # Login upload signup and logout in Senders End
    url(r'^login$', views.log_in, name='login'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^logout$', views.log_out, name='logout'),


      # Url to succesfully download a file from reciever end after entering link password
      url(r'^filesharing$', views.filesharing, name='filesharing'),

    # expiry page for a file shared
    url(r'^userexpiry/(?P<nameoffile>.*)/$', views.userexpiry,name='userexpiry'),    

    # Generated Link Url
    url(r'^(?P<slug>.{32})/$',views.testing,name = 'testing'),
    
    # Admin Specific User Search Url
    url(r'^uadmin/specificuser/$',views.fetch,name = 'fetch'),

    # Paasing Name of Keyword for Admin Search Request using GET Method to Views
    url(r'^uadmin/view=(?P<slug>.*)/$',views.specificuser,name = 'specificuser')

]




