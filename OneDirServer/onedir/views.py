# Create your views here.
import os
import json
import shutil
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields.files import FieldFile
from helpers import getClientIp, userAlreadyExists, getFileSize, getDateTime, getFiles, getHistory, isAdmin
from onedir.models import UserAction
from django.db.models import Q

"""
Views
When a user enters a url, the url is matched to one of the urlpatterns in urls.py (../OneDirServer/urls.py). 
Each defined urlpattern can can call a view, such as those defined below. Views return http responses. 

User
A user is a predefined model in django that comes with a lot of free goodies. 

"""

def index(request):
	if request.user.is_authenticated():
		return HttpResponse("Logged in as %s" % request.user.username)
	else: 
		return HttpResponse("Not logged in")

def logout_user(request):
	if request.user.is_authenticated():
		logout(request)
		return HttpResponse("Logged out successfully")
	else: 
		return HttpResponse("You must be logged in to log out")


def login_user(request):
	if request.POST.get('username') and request.POST.get('password'):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request, user)
			return HttpResponse('Logged in as %s' % user.username)
		else:
			return HttpResponse('User %s does not exist' % username)
	else: 
		return HttpResponse('POST with username and password to login')

def register_user(request):
	if request.POST.get('username') and request.POST.get('password') and request.POST.get('confirmpw'):
		username = request.POST['username']
		password = request.POST['password']
		confirmpw = request.POST['confirmpw']
		if (confirmpw != password):
			return HttpResponse("Passwords do not match!")
		elif userAlreadyExists(username):
			return HttpResponse("User %s already exists!" % username)
		else:
			User.objects.create_user(username, "No email", password)
			login(request, authenticate(username=username, password=password))
			return HttpResponse("User %s created successfully!" % username)
	else: 
		return HttpResponse("POST with username, password, and confirmpw to register")

def add_file(request):
	if not request.user.is_authenticated():
		return HttpResponse("Must be logged in to upload files!")
	if request.method == 'POST':
		path = "../uploads/" + str(request.user.id) + "/" + request.POST['path']
		#Attempt to create directory
		try:
			os.makedirs(path)
		except:
			pass
		key = request.POST['key']
		#If a file is uploaded, write to a new file
		if request.POST.get('filename'):
			new_file = request.FILES['file']
			filename = request.POST['filename']
			path = "../uploads/" + str(request.user.id) + "/" + request.POST['path']
			full_path = path + filename
			cfile = open(full_path, "wb+")
			for chunk in new_file.chunks():
				cfile.write(chunk)
			cfile.close()
			action = UserAction(
				user=request.user, 
				action="add", 
				path=request.POST['path'] + filename, 
				key=key, 
				timestamp=getDateTime(key),
				ip=getClientIp(request)
			)
			action.save()
		#Otherwise, we've already created a directory
		else:
			action = UserAction(
				user=request.user, 
				action="add", 
				path=request.POST['path'], 
				key=key,
				timestamp=getDateTime(key), 
				ip=getClientIp(request)
			)
			action.save()
		return HttpResponse("Great success!")
	return HttpResponse("Failed to upload anything.")

def get_file(request):
	if not request.user.is_authenticated():
		return HttpResponse("Must be logged in to download files!")
	if request.method == 'POST':
		filename = request.POST['filename']
		path = "../uploads/" + str(request.user.id) + "/" + request.POST['path']
		full_path = path + filename
		if os.path.exists(full_path):
			try:
				getfile = open(full_path, "rb")
				full_file = getfile.read()
				getfile.close()
				return HttpResponse(full_file)
			except:
				pass
		else:
			return HttpResponse("File not found!")
	return HttpResponse("Failed to download anything!")

def delete_file(request):
	if not request.user.is_authenticated():
		return HttpResponse("Must be logged in to upload files!")
	if request.method == 'POST':
		try:
			path = "../uploads/" + str(request.user.id) + "/" + request.POST['path']
			if (path[len(path)-1]=="/"):
				shutil.rmtree(path)
			else:
				os.remove(path)
			new_log = UserAction(
				user=request.user, 
				action="delete", 
				path=request.POST['path'], 
				key=request.POST['key'], 
				timestamp=getDateTime(request.POST['key']),
				ip=getClientIp(request)
			)
			new_log.save()
			return HttpResponse("File at %s deleted" % request.POST['path'])
		except:
			return HttpResponse("Failed to delete file at %s" % request.POST['path'])

def get_users(request):
	if not request.user.is_superuser:
		return HttpResponse("You don't have permission!")
	else: 
		user_list = []
		for user in User.objects.all():
			user_list.append(user.username)
		user_list = ",".join(user_list)
		return HttpResponse(user_list)

def get_activity(request):
	if not (request.user.is_superuser or (request.user.username == request.POST['username'])):
		return HttpResponse("You don't have permission!")
	if request.method == 'POST':
		username = request.POST['username']
		user_activity = {}
		for log in UserAction.objects.filter(user__username=username):
			user_array = [log.action, log.path, log.ip]
			user_activity[str(log.timestamp)] = user_array
		json_response = json.dumps(user_activity)
		return HttpResponse(json_response)

def get_sync_log(request):
	if not request.user.is_authenticated():
		return HttpResponse("Must be logged in to sync!")
	if request.method == 'POST':
		username = request.user.username
		time_of_last_sync = request.POST['timestamp']
		user_activity = {}
		for log in UserAction.objects.filter(user__username=username):
			#.exclude(ip=getClientIp(request)):
			user_array = [log.action, log.path]
			user_activity[log.key] = user_array
		json_response = json.dumps(user_activity)
		return HttpResponse(json_response)


"""
These "form" views plug HTTPresponses into templates to create forms in HTML. 
Our client would not want to call these unless finding the CSRF token. 
"""
def login_form(request):
	if request.user.is_authenticated():
		return render(request, "login.html", {'login_failed': False, 'is_authenticated': False})
	else: 
		return render(request, "login.html", {'login_failed': False, 'is_authenticated': False})

def register_form(request):
	return render(request, "register.html")

def logout_browser(request):
	if request.user.is_authenticated():
		logout(request)
	return HttpResponseRedirect('/')

def myprofile(request, username=""):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request, user)
		return HttpResponseRedirect(reverse("onedir.views.myprofile"))

	if request.method == 'GET':
		user = request.user
		if user.id is None:
			return render(request, "login.html", {'login_failed': True, 'is_authenticated': False})

	if user.is_superuser:
		try:
			user2 = User.objects.get(username=username)
			return render(request, "profile.html", {
				'is_admin': True, 
				'files': getFiles(user2.id), 
				'username': user.username, 
				'viewing': True,
				'user2': user2.username,
				'history': getHistory(user2.id)
			})
		except:
			return render(request, "profile.html", {
				'is_admin': True, 
				'files': getFiles(user.id), 
				'username': user.username,
				'history': getHistory(user.id)
			})
	else:
		return render(request, "profile.html", {
			'is_admin': False, 
			'files': getFiles(user.id), 
			'username': user.username,
			'history': getHistory(user.id)
		})

def mypassword(request):
	if not request.user.is_authenticated:
		return render(request, "login.html", {'login_failed': False, 'is_authenticated': False})
	if request.method == 'POST':
		user = request.user
		if request.POST['password'] == request.POST['confirmpw']:
			user.set_password(request.POST['password'])
			user.save()
			return render(request, "profile.html", {
				'is_admin': isAdmin(user.id), 
				'files': getFiles(user.id), 
				'username': user.username,
				'history': getHistory(user.id)
			})
		else:
			return render(request, "password.html", {
				'failed': True,
				'username': user.username,
				'is_admin': isAdmin(user.id),
			})
	if request.method == 'GET':
		user = request.user
		return render(request, "password.html", {
			'username': user.username,
			'is_admin': isAdmin(user.id), 
		})

def theirpassword(request, username=""):
	print "this is called"
	if not request.user.is_authenticated:
		return render(request, "login.html", {'login_failed': False, 'is_authenticated': False})
	if not request.user.is_superuser:
		return HttpResponseRedirect('/password/')
	if request.method == 'POST':
		if request.POST['password'] == request.POST['confirmpw']:
			user = User.objects.get(username=request.POST['username'])
			user.set_password(request.POST['password'])
			user.save()
			user = request.user
			return render(request, "profile.html", {
				'is_admin': isAdmin(user.id), 
				'files': getFiles(user.id), 
				'username': user.username,
				'history': getHistory(user.id)
			})
		else:
			return render(request, "password.html", {
				'failed': True,
				'username': user.username,
				'is_admin': isAdmin(user.id),
				'username2': username,
				'viewing': True,
			})
	if request.method == 'GET':
		user = request.user
		return render(request, "password.html", {
			'username2': username,
			'viewing': True,
			'username': user.username,
			'is_admin': isAdmin(user.id), 
		})

def userlist(request):
	if not request.user.is_authenticated:
		return render(request, "login.html", {'login_failed': False, 'is_authenticated': False})
	if not request.user.is_superuser:
		return HttpResponseRedirect('/myprofile/')
	userlist = []
	for user in User.objects.all():
		userinfo = []
		userinfo.append(user.username)
		userinfo.append(getFileSize(user.id))
		userlist.append(userinfo)
	user = request.user
	return render(request, "userlist.html", {
		'username': user.username,
		'is_admin': isAdmin(user.id),
		'users': userlist,
	})

def systemlist(request):
	if not request.user.is_authenticated:
		return render(request, "login.html", {'login_failed': False, 'is_authenticated': False})
	if not request.user.is_superuser:
		return HttpResponseRedirect('/myprofile/')
	system_size = getFileSize("")
	system_files = getFiles("")
	user = request.user
	return render(request, "system.html", {
		'username': user.username,
		'is_admin': isAdmin(user.id),
		'files': system_files,
		'size': system_size
	})

def ban(request, username=""):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/myprofile/')
	try:
		x = User.objects.get(username=username)
		x.is_active = False
		x.save()
		url = '/myprofile/' + x.username
		return HttpResponseRedirect(url)
	except:
		return HttpResponse('/myprofile/')

def destroy(request, username=""):
	if not request.user.is_superuser:
		return HttpResponseRedirect('/myprofile/')
	try:
		x = User.objects.get(username=username)
		path = "../uploads/" + str(x.id) + "/"
		shutil.rmtree(path)
		url = "/myprofile/" + x.username + "/"
		return HttpResponseRedirect(url)
	except:
		pass
	return HttpResponseRedirect('/myprofile/')
