__author__ = 'axel'
import users
import os
from threading import Thread
import sys
import watchdog_process
import shutil
import time
from address import LOCAL_FOLDER

print sys.argv

home= os.path.expanduser("~")

def resetOnedir():
    if not os.path.exists(LOCAL_FOLDER):
        os.mkdir(LOCAL_FOLDER)
    else:
        shutil.rmtree(LOCAL_FOLDER)
        os.mkdir(LOCAL_FOLDER)
    open('fileMonitorLog.txt', "w").close()

if(sys.argv[1] == 'ui'):
    print home
    while True:
        print 'Welcome to OneDir!\n'
        print 'Please enter the number for a command:\n'
        print '1. Create a new user\n'
        print '2. Log in a user and start onedir: \n'
        print '3. Toggle synchronization'
        userInput = input()
        if(userInput == 1):
            users.logout()
            print 'Please enter a username:'
            username = raw_input()
            print 'Please enter a password:'
            password = raw_input()
            print 'Please enter password again: '
            cwpassword = raw_input()
            response = users.register(username, password, cwpassword)
            if response.__contains__('successfully'):
                print response
                resetOnedir()
                print 'You can now begin using ~/onedir'
            else:
                print response
        if(userInput == 2):
            print 'Please enter a username:'
            username = raw_input()
            print 'Please enter a password:'
            password = raw_input()
            response = users.login(username, password)
            print response
            if response.__contains__('Logged in as'):
                resetOnedir()
                open('fileMonitorLog.txt', 'w').close()
                print 'You can now begin using /onedir/'
                watchdog_process.startWatchdog()
        if(userInput == 3):
            isMonitoring = watchdog_process.getMonitoring()
            if isMonitoring:
                print 'Now turning off onedir. Any changes after this point will not be recorded!'
                watchdog_process.toggleWatchdog()
            else:
                print 'Now turning on onedir!'
                watchdog_process.toggleWatchdog()
                print watchdog_process.getMonitoring()








