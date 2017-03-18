import http.client
import json
import ssl


connection = http.client.HTTPConnection('user.hanjianqiao.cn', 7010)


for i in range(10000):
	connection.request('GET', '/search?catalog=1&activity=0')
	response = connection.getresponse()
	response.read().decode()

print("end")
