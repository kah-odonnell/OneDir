import urllib, urllib2, MultipartPostHandler
import cookielib
from address import ROOT_ADDRESS, LOCAL_FOLDER
from poster.encode import multipart_encode
from datetime import datetime
import time
import json
import os
import shutil

#Build an opener that passes a session cookie with each HTML request
cj = cookielib.CookieJar()
opener = urllib2.build_opener(
    urllib2.HTTPCookieProcessor(cj), 
    MultipartPostHandler.MultipartPostHandler
)

token = None
def get_token():
    """
    Pull a CSRF token off of a django form.
    CSRF tokens are required in POST params for POSTs in django to be valid

    Returns:
        token - the csrftoken
        None - the token could not be grabbed
    """
    global token
    if token is None:
        try:
            login_form = opener.open(ROOT_ADDRESS + "forms/login/").read()
            token = [x.value for x in cj if x.name == 'csrftoken'][0]
        except IndexError:
            token = None
    return token

def login(username, password):
    """
    Logs in a user to the server given a username and password.

    Args:
        username
        password
    Returns:
        (string) server's response
            Logged in as <username>
            User <username> does not exist!
    """
    csrftoken = get_token()
    #Each element in POST params can be grabbed by server with request.POST['param_name']
    values = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrftoken,
    }
    params = urllib.urlencode(values)
    login_page = opener.open(ROOT_ADDRESS + "login/", params).read()
    return login_page


def logout():
    """
    Logs out a user from the server.

    Returns:
        (string) server's response
            Logged out successfully!
            You must be logged in to log out!
    """
    logout_page = opener.open(ROOT_ADDRESS + "logout/").read()
    return logout_page

def register(username, password, confirmpw):
    """
    Register and logs in user on the server with a given username, password, and confirmpw
    Fails if password and confirmpw are not matching

    Args:
        username
        password
        confirmpw

    Returns:
        (string) server's response
            User <username> created succesfully!
            User <username> already exists!
        (string) Passwords do not match!
    """
    csrftoken = get_token()
    if password != confirmpw:
        return "Passwords do not match!"
    values = {
        'username': username,
        'password': password,
        'confirmpw': confirmpw,
        'csrfmiddlewaretoken': csrftoken
    }
    params = urllib.urlencode(values)
    register_page = opener.open(ROOT_ADDRESS + "register/", params).read()
    return register_page

def add_file(file_path, key):
    """
    Attempts to upload a designated file to the server

    Args:
        file_path - (string) path of desired file/folder relative to the location of this python file
        key - (string) generated by watchdog when add event is detected 

    Returns:
        (string) server's response
            Logged in as <username>
            User <username> does not exist
        (string) Error finding <filepath>
    """
    csrftoken = get_token()
    #If file_path ends in a slash, it's a directory
    params = {}
    if file_path[len(file_path)-1] == "/":
        params = {
            "path": file_path,
            "key": key,
            "csrfmiddlewaretoken": csrftoken
        }
    #Otherwise, it's a new file
    else:
        try:
            f = open(LOCAL_FOLDER + file_path, "rb")
        except IOError:
            return "Error finding %s" % file_path
        f = open(LOCAL_FOLDER + file_path, "rb")
        #split directory into a list
        directory_list = file_path.split('/')
        #grab file name from last element
        filename = directory_list[len(directory_list)-1]
        #build path name from every other element
        file_path = "/".join(directory_list[0:len(directory_list)-1]) + "/"
        params = {
            "filename": filename,
            "path": file_path,
            "file": f,
            "key": key,
            "csrfmiddlewaretoken": csrftoken
        }
    file_page = opener.open(ROOT_ADDRESS + "add/", params).read()
    try:
        f.close()
    except:
        pass
    return file_page

def get_file(file_path):
    """
    Downloads a file from the server at a path relative to that user's folder on the server.
    Saves in the designated folder.
        or
    Creates a new folder without contacting the server. 

    Args:
        file_path - (string) path of desired file, relative to user's fodler

    Returns:
        (string) File at <file_path> downloaded
        or
        (string) Error message from the server
    """
    csrftoken = get_token()
    if file_path[len(file_path)-1] == "/":
        try:
            os.makedirs(file_path)
        except:
            pass
        return "New folder created."
    else: 
        full_path = file_path
        #split directory into a list
        directory_list = file_path.split('/')
        #grab file name from last element
        filename = directory_list[len(directory_list)-1]
        #build path name from every other element
        file_path = "/".join(directory_list[0:len(directory_list)-1]) + "/"
        params = {
            "filename": filename,
            "path": file_path,
            "csrfmiddlewaretoken": csrftoken
        }
        server_response = opener.open(ROOT_ADDRESS + "get/", params).read()
        errors = ["File not found!","Must be logged in to download files!"]
        if server_response not in errors:
            try:
                os.makedirs(LOCAL_FOLDER + file_path[1:])
            except:
                pass
            try:
                cfile = open(LOCAL_FOLDER + full_path, "wb+")
            except:
                cfile = open(LOCAL_FOLDER + full_path[1:], "wb+")
            cfile.write(server_response)
            cfile.close()
            return "File at %s downloaded" % full_path
        else:
            return server_response

def delete_file(path, key):
    csrftoken = get_token()
    params = {
        "path": path,
        "key": key,
        "csrfmiddlewaretoken": csrftoken
    }
    delete_page = opener.open(ROOT_ADDRESS + "delete/", params).read()
    return delete_page

def delete_local(path):
    path = LOCAL_FOLDER + path
    try:
        if (path[len(path)-1]=="/"):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except:
        pass
    return "File at %s deleted locally" % path

def get_activity(username):
    csrftoken = get_token()
    params = {
        "username": username,
        "csrfmiddlewaretoken": csrftoken
    }
    activity_page = opener.open(ROOT_ADDRESS + "activity/", params).read()
    return "Activity for %s: " % username + "\n" + activity_page 

def get_sync_log(timestamp):
    csrftoken = get_token()
    params = {
        "timestamp": timestamp, 
        "csrfmiddlewaretoken": csrftoken
    }
    sync_json = opener.open(ROOT_ADDRESS + "sync/", params).read()
    try:
        sync_dict = json.loads(sync_json)
    except:
        sync_dict = {}
    return sync_dict