```
sudo dpkg-reconfigure locales
```



nohup python3 set_server.py 1>set.out.log 2>set.err.log &

nohup python3 get_server.py 1>get.out.log 2>get.err.log &

nohup python3 bill/app.py 1>bil.out.log 2>bil.err.log &

nohup python3 message/app.py 1>mes.out.log 2>mes.err.log &

nohup python3 good/app.py 1>goo.out.log 2>goo.err.log &

nohup python3 recommend/app.py 1>rec.out.log 2>rec.err.log &

nohup python3 periodic.py 1>per.out.log 2>per.err.log &

nohup python3 charger/app.py 1>cha.out.log 2>cha.err.log &

nohup python user/app.py 1>use.out.log 2>use.err.log &

nohup python3 app/app/py 1>app.out.log 2>app.err.log &