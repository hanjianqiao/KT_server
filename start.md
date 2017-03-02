```
sudo dpkg-reconfigure locales
```



nohup python3 set_server.py 1>/dev/null 2>set.log &

nohup python3 get_server.py 1>/dev/null 2>get.log &

nohup python3 bill/app.py 1>/dev/null 2>bil.log &

nohup python3 message/app.py 1>/dev/null 2>mes.log &

nohup python3 good/app.py 1>/dev/null 2>goo.log &

nohup python3 recommend/app.py 1>/dev/null 2>rec.log &

nohup python3 periodic.py 1>/dev/null 2>per.log &

nohup python3 charger/app.py 1>/dev/null 2>cha.log &

nohup python user/app.py 1>/dev/null 2>use.log &