# -*- coding: utf-8 -*- 
#!/usr/bin/python3

import threading
import time
import http.client
import json
import ssl
import sys
import random


class myThread (threading.Thread):
    def __init__(self, threadID, name, address, port, method, path, delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.address = address
        self.port = port
        self.method = method
        self.path = path
        self.delay = delay
    def run(self):
        connection = http.client.HTTPConnection(self.address, self.port)
        headers = {'Content-type': 'application/json'}
        foo = { 'foo': 'foo'}
        json_foo = json.dumps(foo)
        while(1):
            connection.request(self.method, self.path, json_foo, headers)
            response = connection.getresponse()
            print(response.read().decode())
            time.sleep(self.delay)


# Create new threads
thread1 = myThread(1, 'check user unbuy', 'localhost', 10010, 'POST', '/hourlycheck', 1200)
thread2 = myThread(2, 'Expire good self', 'localhost', 13000, 'GET', '/check', 24*60*60)
thread3 = myThread(3, 'Expire good shop', 'localhost', 14000, 'GET', '/check', 24*60*60)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

# Wait for all threads to complete
thread1.join()
thread2.join()
thread3.join()

print ("Exiting Main Thread")
