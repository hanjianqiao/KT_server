# -*- coding: utf-8 -*- 
#!/usr/bin/python3

import http.client
import json


connection = http.client.HTTPConnection('localhost', 13000)
headers = {'Content-type': 'application/json'}
foo = { 'foo': 'foo'}
json_foo = json.dumps(foo)
connection.request('GET', '/check', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())
