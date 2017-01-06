import _thread
import time
import requests
import threading

class myThread (threading.Thread):
    def __init__(self, tpath):
        threading.Thread.__init__(self)
        self.tpath = tpath
    def run(self):
        print_time(self.tpath)


# 为线程定义一个函数
def print_time(tpath):
   count = 0
   url = tpath # Set destination URL here
   r = ""
   while count < 10:
      count += 1
      r = requests.post(tpath)
   #print(r)
#print("times: " + str(count) + " do " + tpath + " " + r.text)

threads = []

for i in range(100):
    threads.append(myThread("http://kouchenvip.com:5000/inc"))
    threads.append(myThread("http://kouchenvip.com:5001/dec"))

for t in threads:
    t.start()
# Wait for all threads to complete
while 1:
    pass
print ("Exiting Main Thread")

