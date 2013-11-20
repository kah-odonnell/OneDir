from django.contrib.auth.models import User
from datetime import datetime
import os

def getClientIp(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#A test to see whether a user already exists in the database
def userAlreadyExists(username):
	try:
		User.objects.filter(username=username).get()
	except:
		return False
	return True

def getDateTime(key):
	try:
		timestamp = datetime.strptime(key, "%Y-%m-%d %H:%M:%S.%f")
		return timestamp
	except:
		key = key[0:(len(key)-2)]	
		timestamp = datetime.strptime(key, "%Y-%m-%d %H:%M:%S.%f")
		return timestamp

def getFiles(id):
	file_list = []
	directory = "../uploads/" + str(id)
	print directory
	os.walk(directory, topdown=False)
	for root, dirs, files in os.walk(directory, topdown=True):
		print str(root) + "|" + str(dirs) + "|" + str(files)
		for name in files:
			print name
			file_list.append(name)
		for name in dirs:
			print name
			file_list.append(name + "/")
	return file_list
