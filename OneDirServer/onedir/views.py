# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


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

@csrf_exempt
def register_user(request):
	if request.POST.get('username') and request.POST.get('password') and request.POST.get('confirmpw'):
		username = request.POST['username']
		password = request.POST['password']
		confirmpw = request.POST['confirmpw']
		if (confirmpw != password):
			return HttpResponse("Passwords do not match!")
		elif userAlreadyExists(username):
			return HttpResponse("User already exists!")
		else:
			User.objects.create_user(username, "No email", password)
			login(request, authenticate(username=username, password=password))
			return HttpResponse("User %s created successfully!" % username)
	else: 
		return HttpResponse("POST with username, password, and confirmpw to register")


"""
These "form" views plug HTTPresponses into templates to create forms in HTML. Our client would not want to
call these. 
"""

def login_form(request):
	if request.user.is_authenticated():
		return render(request, "login.html", {'is_authenticated': True, 'username': request.user.username})
	else: 
		return render(request, "login.html", {'is_authenticated': False})

def register_form(request):
	return render(request, "register.html")