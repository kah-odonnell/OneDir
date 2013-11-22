from django.contrib.auth.models import User
from onedir.models import UserAction
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

def getHistory(theid):
	history = []
	for log in UserAction.objects.filter(user=theid):
		user_array = [log.action, log.path, log.timestamp]
		history.append(user_array)
	return history

def getFiles(id):
	file_list = []
	directory = "../uploads/" + str(id)
	file_list = [getDirectoryStructure(directory)]
	thelist = []
	return printStructure(file_list, 0, thelist)

def getDirectoryStructure(path):
	file_list = []
	i = 0
	try:
		for filename in os.listdir(path):
			file_list.append(filename)
			x = getDirectoryStructure(path + "/" + filename)
			if x:
				file_list.append(x)
	except:
		pass
	return file_list

def getFileSize(userid):
    total_size = 0
    start_path = "../uploads/" + str(userid)
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def printStructure(file_list, depth, thelist):
	whitespace = ""
	for i in range(0, depth):
		whitespace = whitespace + "     "
	for item in file_list:
		if isinstance(item, list):
			printStructure(item, depth + 1, thelist)
		else:
			thelist.append(whitespace + item) 
	return thelist

def isAdmin(id):
	user = User.objects.get(id=id)
	if user.is_superuser:
		return True
	else:
		return False



