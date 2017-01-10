import http.client
import json
import ssl

context = ssl._create_unverified_context()


connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)

headers = {'Content-type': 'application/json'}

#foo = {'text': 'Hello world github/linguist#1 **cool**, and #1!'}
#json_foo = json.dumps(foo)
json_foo = '{"user_id":"15913101318","password":"123456","code":"100000", "email":"1@2.com", "amount":"1000"}'

connection.request('POST', '/register', json_foo, headers)
response = connection.getresponse()

print(response.read().decode())
