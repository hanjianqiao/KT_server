import http.client
import json
import ssl

context = ssl._create_unverified_context()


connection = http.client.HTTPSConnection('user.hanjianqiao.cn', 10010, context = context)

headers = {'Content-type': 'application/json'}

foo = {	'user_id': '13450205512',
		'amount':'8000'}
json_foo = json.dumps(foo)

connection.request('POST', '/charge', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())
