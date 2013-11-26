from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from onedir import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'OneDirServer.views.home', name='home'),
    # url(r'^OneDirServer/', include('OneDirServer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', views.login_form),
    url(r'^logout/', views.logout_user),
    url(r'^login/', views.login_user),
    url(r'^register/', views.register_user),
    url(r'^forms/register/', views.register_form),
    url(r'^forms/login/', views.login_form),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add/', views.add_file),
    url(r'^users/', views.get_users),
    url(r'^get/', views.get_file),
    url(r'^delete/', views.delete_file),
    url(r'^activity/', views.get_activity),
    url(r'^sync/', views.get_sync_log),
    url(r'^myprofile/(?P<username>.*)', views.myprofile),
    url(r'^myprofile/', views.myprofile),
    url(r'^logoutbrowser/',views.logout_browser),
    url(r'^password/$', views.mypassword),
    url(r'^password/(?P<username>.*)', views.theirpassword),
    url(r'^userlist/', views.userlist),
    url(r'^system/', views.systemlist),
    url(r'^ban/(?P<username>.*)', views.ban),
    url(r'^destroy/(?P<username>.*)', views.destroy),
)
