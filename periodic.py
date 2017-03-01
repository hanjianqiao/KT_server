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
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        connection = http.client.HTTPConnection('localhost', 10010)
        headers = {'Content-type': 'application/json'}
        foo = { 'foo': 'foo'}
        json_foo = json.dumps(foo)
        while(1):
            connection.request('POST', '/hourlycheck', json_foo, headers)
            response = connection.getresponse()
            print(response.read().decode(), file=sys.stderr)
            time.sleep(1800+int(random.random()*1000))


# Create new threads
thread1 = myThread(1, "Thread-1", 1)

# Start new Threads
thread1.start()

# Wait for all threads to complete
thread1.join()

print ("Exiting Main Thread")
