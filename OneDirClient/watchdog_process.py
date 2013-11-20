import time
import os
from datetime import datetime, MINYEAR
import json
import re
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.utils.dirsnapshot import DirectorySnapshot
from watchdog.utils.dirsnapshot import DirectorySnapshotDiff
from address import LOCAL_FOLDER
from users import *
from threading import Thread

def getLocalLog():
    fileLogLoc = "fileMonitorLog.txt"
    f = open(fileLogLoc, "rw+")
    log_dictionary = {}
    string = ""
    while True:
        c = f.read(1)
        if c != "}":
            string = string + c
        if c == "}":
            string = string + c
            mini_dict = json.loads(string)
            string = ""
            log_dictionary = dict(log_dictionary.items() + mini_dict.items())
        if not c:
            f.truncate()
            return log_dictionary

def getServerLog():
    fileSyncLast = "lastSync.txt"
    f = open(fileSyncLast, "rw+")
    last_time = f.read()
    if last_time == "":
        last_time = str(datetime(MINYEAR, 1, 1, tzinfo=None))
    f.close()

    timestamp = str(datetime.now())

    f = open(fileSyncLast, "r+")
    f.write(timestamp)
    f.close()
    log = get_sync_log(last_time)
    return log

def sync():
    """
    Sync compares differences between the log of the server and the log of the client...
    If there are "add" logs on the server that aren't on the client, 
    the client gets those files.
    If there are "delete" logs on the server that aren't on the client,
    the client deletes those files (locally)
    It also creates a dummy log with the same key as those on the server, so that
    they are no longer recognized as a difference between the two logs
    """
    server_log = getServerLog()
    local_log = getLocalLog()
    for key in server_log:
        if key in local_log:
            pass
        else:
            now = datetime.now()
            path = server_log.get(key)[1]
            if server_log.get(key)[0] == "add":
                get_file(path)
                log_entry = {key: "Dummy Log!"}
                log(json.dumps(log_entry))
            if server_log.get(key)[0] == "delete":
                delete_local(path)
                log_entry = {key: "Dummy Log!"}
                log(json.dumps(log_entry))


def log(output):
    fileLogLoc = "fileMonitorLog.txt"
    if (output[0]=="{"):
        with open(fileLogLoc, "a") as myfile:
            myfile.write(output)

def getRelativePath(parent):
    prefix_len = len(LOCAL_FOLDER) - 1
    path = parent[prefix_len:]
    return path

def monitorFileModifications(previousSnap, currentSnap):
    item = 0
    for path, stat_info in currentSnap.stat_snapshot.items():
        if path in previousSnap.stat_snapshot:
            ref_stat_info = previousSnap.stat_info(path)
            if stat_info.st_mtime != ref_stat_info.st_mtime and os.path.isfile(path):
                #Counting file modifications like a regular add
                
                rel_path = getRelativePath(path)
                now = datetime.now()
                key = str(now)+str(item)
                log_items = ["add", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                print add_file(rel_path, key)
                print 'This file was modified: ' + path
                
        item = item + 1

def fileMonitor(n):
    path = LOCAL_FOLDER
    previousSnap = DirectorySnapshot(path, True)
    while True:
        dirSnap = DirectorySnapshot(path, True)
        dirSnapDiff = DirectorySnapshotDiff(previousSnap, dirSnap)
        sync()
        if dirSnapDiff.dirs_created.__len__() is not 0:
            item = 0
            for parent in dirSnapDiff.dirs_created:
                now = datetime.now()
                rel_path = getRelativePath(parent) + "/"
                key = str(now)+str(item)
                log_items = ["add", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print add_file(rel_path, key)
            print 'Directory Created: ' + dirSnapDiff.dirs_created.__str__()

        if dirSnapDiff.dirs_deleted.__len__() is not 0:
            item = 0
            for parent in dirSnapDiff.dirs_deleted:
                now = datetime.now()
                key = str(now)+str(item)
                rel_path = getRelativePath(parent) + "/"
                log_items = ["delete", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print delete_file(rel_path, key)
            print 'Directory Deleted: ' + dirSnapDiff.dirs_deleted.__str__()

        if dirSnapDiff.files_created.__len__() is not 0:
            item = 0
            for parent in dirSnapDiff.files_created:
                now = datetime.now()
                key = str(now)+str(item)
                rel_path = getRelativePath(parent)
                log_items = ["add", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print add_file(rel_path, key)
            print 'File Created: ' + dirSnapDiff.files_created.__str__()

        if dirSnapDiff.files_deleted.__len__() is not 0:
            item = 0
            for parent in dirSnapDiff.files_deleted:
                now = datetime.now()
                key = str(now)+str(item)
                rel_path = getRelativePath(parent)
                log_items = ["delete", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print delete_file(rel_path, key)
            print 'File Deleted: ' + dirSnapDiff.files_deleted.__str__()

        if dirSnapDiff.dirs_moved.__len__() is not 0:
            item = 0
            for parent in dirSnapDiff.dirs_moved:
                original = parent[0]
                new = parent[1]

                now = datetime.now()
                key = str(now)+str(item)
                rel_path = getRelativePath(original) + "/"
                log_items = ["delete", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print delete_file(rel_path, key)

                key = str(now)+str(item)
                rel_path = getRelativePath(new) + "/"
                log_items = ["add", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print add_file(rel_path, key)

        if dirSnapDiff.files_moved.__len__() is not 0:
            for parent in dirSnapDiff._files_moved:
                original = parent[0]
                new = parent[1]

                now = datetime.now()
                key = str(now)+str(item)
                rel_path = getRelativePath(original)
                log_items = ["delete", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print delete_file(rel_path, key)

                key = str(now)+str(item)
                rel_path = getRelativePath(new)
                log_items = ["add", rel_path]
                log_entry = {key: log_items}
                log(json.dumps(log_entry))
                item = item + 1
                print add_file(rel_path, key)

            print 'File Moved: ' + dirSnapDiff.files_moved.__str__()

        monitorFileModifications(previousSnap, dirSnap)
        previousSnap = DirectorySnapshot(path, True)
        time.sleep(n)

if __name__ == '__main__':
    print register("test14","password","password")
    print getLocalLog()
    print getServerLog()
    t = Thread(target=fileMonitor, args=(1,))
    t.start()