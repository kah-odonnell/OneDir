import urllib, urllib2, MultipartPostHandler
import cookielib
from address import ROOT_ADDRESS
from poster.encode import multipart_encode

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

def add_file(file_path):
    """
    Attempts to upload a designated file to the server

    Args:
        file_path - (string) path of desired file relative to the location of this python file

    Returns:
        (string) server's response
            Logged in as <username>
            User <username> does not exist
        (string) Error finding <filepath>
    """
    csrftoken = get_token()
    try:
        f = open(file_path, "rb")
    except IOError:
        return "Error finding %s" % file_path
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
        "csrfmiddlewaretoken": csrftoken
    }
    file_page = opener.open(ROOT_ADDRESS + "add/", params).read()
    f.close()
    return file_page

def get_file(file_path):
    """
    Downloads a file from the server at a path relative to that user's folder on the server.
    Saves in the designated folder

    Args:
        file_path - (string) path of desired file, relative to user's fodler

    Returns:
        (string) server's response
            Logged in as <username>
            User <username> does not exist
        (string) Error finding <filepath>
    """
    csrftoken = get_token()
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
            os.makedirs(filepath)
        except:
            pass
        cfile = open(full_path, "wb+")
        cfile.write(file_page)
        cfile.close()
        return "File at %s downloaded" % full_path
    else:
        return server_response

def get_users():
    user_page = opener.open(ROOT_ADDRESS + "users/").read()
    return "Users: " + user_page

def get_activity(username):
    csrftoken = get_token()
    params = {
        "username": username,
        "csrfmiddlewaretoken": csrftoken
    }
    activity_page = opener.open(ROOT_ADDRESS + "activity/", params).read()
    return "Activity for %s: " % username + "\n" + activity_page 
