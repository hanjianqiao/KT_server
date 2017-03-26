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
    while count < 100:
        data = {'user_id': '13450205512', 'password': '1hanjianqiao', 'code': inviter_code, 'email': str(id_from+count)+'@2.com'}
        count += 1
        r = requests.get(tpath, data=json.dumps(data), headers=headers, verify=False)
        time.sleep(1)
        print(count)
        #print(r.text)
    #print("times: " + str(count) + " do " + tpath + " " + r.text)

threads = []

for i in range(200):
    threads.append(myThread("http://self.vsusvip.com:7008/search?key=衬衫", 13450200000+i*20, "666666"))

for t in threads:
    t.start()
# Wait for all threads to complete

for t in threads:
    t.join()
print ("Exiting Join")

