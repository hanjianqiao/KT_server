nohup python3 set_server.py 2>set.log &

nohup python3 get_server.py 2>get.log &

nohup python3 bill/app.py 2>bil.log &

nohup python3 message/app.py 2>mes.log &

nohup python3 good/app.py 2>goo.log &

nohup python3 recommend/app.py 2>rec.log &

nohup python3 periodic.py 2>per.log &

nohup python3 charger/app.py 2>cha.log &

nohup python3 user/app.py 2>use.log &