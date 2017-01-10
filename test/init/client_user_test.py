import http.client
import json
import ssl

context = ssl._create_unverified_context()


connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10000, context = context)

headers = {'Content-type': 'application/json'}

foo = {	'user_id': '13450000000',
		'password':'123456',
		'code':'100000',
		'email':'1@0.0000',
		'combo':'1'}
json_foo = json.dumps(foo)

connection.request('POST', '/register', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/query', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/login', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/charge', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/up2vip', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/extendvip', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/extendagent', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/uplevel', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())