import http.client
import json
import ssl

context = ssl._create_unverified_context()


connection = http.client.HTTPSConnection('secure.hanjianqiao.cn', 30001, context = context)

headers = {'Content-type': 'application/json'}

foo = {	'title': '狗狗零食',
		'image':'https://img.alicdn.com/bao/uploaded/i4/TB1xwMgPXXXXXcNXFXXXXXXXXXX_!!0-item_pic.jpg_430x430q90.jpg',
		'comment':'狗狗零食1300g大礼包泰迪宠物磨牙棒咬胶骨头幼犬牛肉条粒鸡胸肉',
		'price':'123.00',
		'url':'https://detail.tmall.com/item.htm?id=21603564234'}
json_foo = json.dumps(foo)

connection.request('POST', '/add', json_foo, headers)
response = connection.getresponse()
print(response.read().decode())
