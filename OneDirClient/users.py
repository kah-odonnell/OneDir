import urllib2
import urllib

def makeUser(url):
	username = raw_input("Username: ")
	password = raw_input("Password: ")
	confirmpw = raw_input("Confirm Password: ")
	userinfo = {"username": username, "password": password, "confirmpw":confirmpw}
	data = urllib.urlencode(userinfo)
	try:
		response = urllib2.urlopen(url, data)
		return response.read()
	except urllib2.URLError:
		return "Didn't work"

if __name__ == "__main__":
	url = "http://localhost:8000/register/"
	print makeUser(url)
