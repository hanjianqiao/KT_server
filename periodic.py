#!/usr/bin/python3

import threading
import time
import http.client
import json
import ssl
import sys


class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        context = ssl._create_unverified_context()
        connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 10010, context = context)
        headers = {'Content-type': 'application/json'}
        foo = { 'user_id': '13450000002'}
        json_foo = json.dumps(foo)
        while(1):
            connection.request('POST', '/hourlycheck', json_foo, headers)
            response = connection.getresponse()
            print(response.read().decode(), file=sys.stderr)
            time.sleep(600)



class myThread2 (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        context = ssl._create_unverified_context()
        connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 30000, context = context)
        headers = {'Content-type': 'application/json'}
        foo = { 'user_id': '13450000002'}
        json_foo = json.dumps(foo)
        while(1):
            connection.request('POST', '/add', json_foo, headers)
            response = connection.getresponse()
            print(response.read().decode(), file=sys.stderr)
            time.sleep(60*60*48)


# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread2(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

# Wait for all threads to complete
thread1.join()
thread2.join()

print ("Exiting Main Thread")