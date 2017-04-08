# -*- coding: utf-8 -*- 
#!/usr/bin/python3

import http.client
import json


connection = http.client.HTTPConnection('localhost', 10010)
headers = {'Content-type': 'application/json'}
foo = { 'foo': 'foo'}
json_foo = json.dumps(foo)
connection.request('POST', '/hourlycheck', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())
