import http.client
import json
import ssl


connection = http.client.HTTPConnection('self.vsusvip.com', 7008)


for i in range(100):
	for j in range(100):
		print(j)
		connection.request('GET', u'/search?key=衬衫')
		response = connection.getresponse()
		response.read().decode()
print("end")
