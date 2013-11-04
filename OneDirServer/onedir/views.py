# Create your views here.
import os
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields.files import FieldFile

from onedir.models import UserAction


#A test to see whether a user already exists in the database
def userAlreadyExists(username):
	try:
		User.objects.filter(username=username).get()
	except:
		return False
	return True

"""
Views
When a user enters a url, the url is matched to one of the urlpatterns in urls.py (../OneDirServer/urls.py). 
Each defined urlpattern can can call a view, such as those defined below. Views return http responses. 

User
A user is a predefined model in django that comes with a lot of free goodies. 

Model

	
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
		new_file = request.FILES['file']
		filename = request.POST['filename']
		path = "../uploads/" + str(request.user.id) + "/" + request.POST['path']
		full_path = path + filename
		try:
			os.makedirs(path)
		except:
			pass
		cfile = open(full_path, "wb+")
		for chunk in new_file.chunks():
			cfile.write(chunk)
		cfile.close()
		action = UserAction(user=request.user, action="add", path=request.POST['path'] + filename )
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
			getfile = open(full_path, "rb")
			full_file = getfile.read()
			getfile.close()
			return HttpResponse(full_file)
		else:
			return HttpResponse("File not found!")
	return HttpResponse("Failed to download anything!")

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
	if not request.user.is_superuser:
		return HttpResponse("You don't have permission!")
	if request.method == 'POST':
		username = request.POST['username']
		user_activity = []
		for log in UserAction.objects.filter(user__username=username):
			user_activity.append(log.action + " | " + str(log.timestamp) + " | " + log.path)
		user_activity = "\n".join(user_activity)
		return HttpResponse(user_activity)

"""
These "form" views plug HTTPresponses into templates to create forms in HTML. 
Our client would not want to call these unless finding the CSRF token. 
"""
def login_form(request):
	if request.user.is_authenticated():
		return render(request, "login.html", {'is_authenticated': True, 'username': request.user.username})
	else: 
		return render(request, "login.html", {'is_authenticated': False})

def register_form(request):
	return render(request, "register.html")