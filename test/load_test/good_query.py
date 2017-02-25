import http.client
import json
import ssl


connection = http.client.HTTPConnection('secure.hanjianqiao.cn', 80)


for i in range(1000):
	connection.request('GET', '/query?id=22')
	response = connection.getresponse()
	print(response.read().decode())

print("end")
