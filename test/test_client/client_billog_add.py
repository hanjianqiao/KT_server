import http.client
import json
import ssl

context = ssl._create_unverified_context()


connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 40000, context = context)

headers = {'Content-type': 'application/json'}

foo = {	'userid': '13450205512',
		'action':'drawback',
		'amount':'1000'}
json_foo = json.dumps(foo)

connection.request('POST', '/add', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())
