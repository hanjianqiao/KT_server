import http.client
import json
import ssl

# headers
headers = {'Content-type': 'application/json'}

def register(userid, password, inviter, email):
    # create user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "password":password,
            "inviter":inviter,
            "email":email}
    json_foo = json.dumps(foo)
    connection.request('POST', '/registerbyid', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return

def charge(userid, amount):
    # charge user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "amount":amount}
    json_foo = json.dumps(foo)
    connection.request('POST', '/charge', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return

def uplevel(userid):
    # charge user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid}
    json_foo = json.dumps(foo)
    connection.request('POST', '/uplevel', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return

def up2vip(userid, year, month, day, fee):
    # vip user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "expire_year":year,
            "expire_month":month,
            "expire_day":day,
            "fee":fee}
    json_foo = json.dumps(foo)
    connection.request('POST', '/up2vip', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return

def extendvip(userid, extend_month, fee):
   # extend vip user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "extend_month":extend_month,
            "fee":fee}
    json_foo = json.dumps(foo)
    connection.request('POST', '/extendvip', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return

def extendagent(userid, level, invitation, extend, fee):
    # agent user
    # create a unverified https connection to set server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10010, context = context)
    foo = { "user_id":userid,
            "level":level,
            "invitation":invitation,
            "extend":extend,
            "fee":fee}
    json_foo = json.dumps(foo)
    connection.request('POST', '/extendagent', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return

def query(userid, password):
    # create user
    # create a unverified https connection to get server
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 10000, context = context)
    foo = { "user_id":userid,
            "password":password}
    json_foo = json.dumps(foo)
    connection.request('POST', '/query', json_foo, headers)
    response = connection.getresponse()
    print(response.read().decode())
    connection.close()
    return


user = '13450000000'
passwd = '123456'
inviter = '13800000000'
email = user+'@'+passwd+'.'+inviter

register(user, passwd, inviter, email)
charge(user, '1000')
up2vip(user, '2018', '10', '10', '100')
extendvip(user, '12', '100')
extendagent(user, 'level1', '100', '100', '200')
uplevel(user)
query(user, passwd)

