import http.client
import json
import ssl

context = ssl._create_unverified_context()


connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 10000, context = context)

headers = {'Content-type': 'application/json'}

foo = {	'user_id': '13450000003',
		'password':'1234fsffefefafasdfsdfsdfsad56',
		'code':'100001',
		'email':'1@3.0000',
		'combo':'1'}
json_foo = json.dumps(foo)

print(json_foo)

connection.request('POST', '/register', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.request('POST', '/login', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())
