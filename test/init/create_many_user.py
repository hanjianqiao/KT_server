import _thread
import time
import requests
import threading
import json

class myThread (threading.Thread):
    def __init__(self, tpath, id_from, inviter_code):
        threading.Thread.__init__(self)
        self.tpath = tpath
        self.id_from = id_from
        self.inviter_code = inviter_code
    def run(self):
        print_time(self.tpath, self.id_from, self.inviter_code)


# 为线程定义一个函数
def print_time(tpath, id_from, inviter_code):
    count = 0
    url = tpath # Set destination URL here
    r = ""
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    while count < 10:
        data = {'user_id': str(id_from + count), 'password': '123456', 'code': inviter_code, 'email': str(id_from+count)+'@2.com'}
        count += 1
        r = requests.post(tpath, data=json.dumps(data), headers=headers)
        print(r.text)
    #print("times: " + str(count) + " do " + tpath + " " + r.text)

threads = []

for i in range(10):
    threads.append(myThread("http://secure.hanjianqiao.cn:5001/register", 13450200000+i*20, "666666"))

for t in threads:
    t.start()
# Wait for all threads to complete
while 1:
    pass
print ("Exiting Main Thread")

