import http.client
import json
import ssl

# create a unverified https connection to set server
context = ssl._create_unverified_context()
connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)

# headers
headers = {'Content-type': 'application/json'}

# create user
foo = { "user_id":"15913101318",
        "password":"123456",
        "code":"100000",
        "email":"1@2.com"}
json_foo = json.dumps(foo)
connection.request('POST', '/register', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

# charge user
foo = { "user_id":"15913101318",
        "amount":"1000"}
json_foo = json.dumps(foo)
connection.request('POST', '/charge', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

# vip user
foo = { "user_id":"15913101318",
        "expire_year":"2018",
        "expire_month":"2",
        "expire_day":"12",
        "fee":"2000"}
json_foo = json.dumps(foo)
connection.request('POST', '/up2vip', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

# extend vip user
foo = { "user_id":"15913101318",
        "extend_month":"33",
        "fee":"89102"}
json_foo = json.dumps(foo)
connection.request('POST', '/extendvip', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

# agent user
foo = { "user_id":"15913101318",
        "extend_month":"123456",
        "invitation":"5",
        "extend":"10",
        "fee":"3000"}
json_foo = json.dumps(foo)
connection.request('POST', '/extendagent', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.close()

# create a unverified https connection to get server
context = ssl._create_unverified_context()
connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10000, context = context)


# agent user
foo = { "user_id":"15913101318",
        "password":"123456"}
json_foo = json.dumps(foo)
connection.request('POST', '/query', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())

connection.close()
