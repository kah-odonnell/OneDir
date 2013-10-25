import urllib, urllib2
import cookielib
from address import ROOT_ADDRESS

cj = cookielib.CookieJar()
opener = urllib2.build_opener(
    urllib2.HTTPCookieProcessor(cj), 
    urllib2.HTTPHandler(debuglevel=1)
)
token = None

def get_token():
	global token
    login_form = opener.open(ROOT_ADDRESS + "forms/login").read()
    if token is None:
        try:
            token = [x.value for x in cj if x.name == 'csrftoken'][0]
        except IndexError:
            token = None
    return token

def login(username, password):
    csrftoken = get_token()
    values = {
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': csrftoken,
    }
    params = urllib.urlencode(values)
    login_page = opener.open(ROOT_ADDRESS + "login/", params).read()
    return login_page

def register(username, password, confirmpw):
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

def index():
    index_page = opener.open(ROOT_ADDRESS).read()
    return index_page