import http.client
import json
import ssl


users = []
for i in range(20):
    users.append(str(13450200000+i*10))

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

# 假定每个用户注册后均充值10000

# 1、  系统邀请注册用户A
# 2、  系统邀请注册用户B
# 3、  A升级VIP
# 4、  B升级VIP
# 5、  B升级代理2000邀请2000续费
# 6、  B邀请注册用户C
# 7、  B邀请注册用户D
# 8、  C升级VIP
# 9、  C升级代理100邀请100续费
# 10、 D升级VIP
# 11、 D升级代理1000邀请1000续费
# 12、 A邀请注册用户E
# 13、 B邀请注册用户F、G、H
# 14、 C邀请注册用户I、J、K、
# 15、 E、F、G、H、I、J、K升级会员


register(users[0], "123456", "13800000000", "0@2.3")
charge(users[0],"10000")
register(users[1], "123456", "13800000000", "1@2.3")
charge(users[1],"10000")
up2vip(users[0], "2018", "02", "12", "300")
up2vip(users[1], "2018", "02", "12", "300")
extendagent(users[1], "level1", "2000", "2000", "9000")
register(users[2], "123456", users[1], "2@2.3")
charge(users[2],"10000")
register(users[3], "123456", users[1], "3@2.3")
charge(users[3],"10000")
up2vip(users[2], "2018", "02", "12", "300")
extendagent(users[2], "level1", "100", "100", "900")
up2vip(users[3], "2018", "02", "12", "300")
extendagent(users[3], "level1", "1000", "1000", "9000")
register(users[4], "123456", users[0], "4@2.3")
charge(users[4],"10000")
up2vip(users[4], "2018", "02", "12", "300")
register(users[5], "123456", users[1], "5@2.3")
charge(users[5],"10000")
up2vip(users[5], "2018", "02", "12", "300")
register(users[6], "123456", users[1], "6@2.3")
charge(users[6],"10000")
up2vip(users[6], "2018", "02", "12", "300")
register(users[7], "123456", users[1], "7@2.3")
charge(users[7],"10000")
up2vip(users[7], "2018", "02", "12", "300")
register(users[8], "123456", users[2], "8@2.3")
charge(users[8],"10000")
up2vip(users[8], "2018", "02", "12", "300")
register(users[9], "123456", users[2], "9@2.3")
charge(users[9],"10000")
up2vip(users[9], "2018", "02", "12", "300")
register(users[10], "123456", users[2], "10@2.3")
charge(users[10],"10000")
up2vip(users[10], "2018", "02", "12", "300")
for i in range(11):
    uplevel(users[i])

