# Build new server from Ali-yun

## 1. Buy new instance

## 2. User setup

```shell
# SSH as root
adduser lct
usermod -aG sudo lct
passwd lct
logout
```



## 3. Install dependencies

```Shell
# login as lct
# configure locales
sudo dpkg-reconfigure locales
# install apache and configure
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod ssl
sudo a2enmod wsgi
# install nginx
wget http://nginx.org/keys/nginx_signing.key
sudo apt-key add nginx_signing.key
sudo vim /etc/apt/sources.list
## add following to the end of file
## deb http://nginx.org/packages/ubuntu/ xenial nginx
## deb-src http://nginx.org/packages/ubuntu/ xenial nginx
sudo apt update
sudo apt install nginx
# install python (apache2 uses python3)
sudo -H pip3 install -r 'requirements-dev.txt'  -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
```



## Configure servers

### Self-Choose good server

### Apache

```shell
sudo vim /etc/apache2/sites-enabled/000-default.conf
```

add following to the file

```
# self good server
<VirtualHost *:13000>
	DocumentRoot /home/lct/user.server/good/
	WSGIScriptAlias / /home/lct/user.server/good/apache_self_good.wsgi
	<Directory /home/lct/user.server/good/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/self.good.error.log
	LogLevel warn
	CustomLog /home/lct/logs/self.good.access.log combined
</VirtualHost>
```

```shell
sudo vim /etc/apache2/apache2.conf
# add "ServerName DomainName" on the top
# DomainName: like "secure.hanjianqiao.cn"
sudo vim /etc/apache2/ports.conf
# port listen 13000
mkdir /home/lct/logs
chmod 777 /home/lct/logs
```

Configure folder

```shell
sudo groupadd varwwwusers
sudo chgrp -R varwwwusers /home/lct/user.server/good
sudo adduser www-data varwwwusers
sudo chmod -R 770 /home/lct/user.server/good/
sudo usermod -a -G varwwwusers lct
git config core.filemode false
```

Restart Apache

```shell
sudo apache2ctl restart
```

#### Nginx

```shell
sudo vim /etc/nginx/conf.d/nginx_self_good.conf

# start nginx
sudo nginx

# reload config
sudo nginx -s reload 
```

File:

```
# nginx_self_good.conf
server {
    listen          7008;
    server_name     self.vsusvip.com;
    location / {
        proxy_pass http://localhost:13000;
    }
}
```



### Recommend good server

### Apache

```shell
sudo vim /etc/apache2/sites-enabled/000-default.conf
```

add following to the file

```
# rec good server
<VirtualHost *:14000>
	DocumentRoot /home/lct/user.server/recommend/
	WSGIScriptAlias / /home/lct/user.server/recommend/apache_rec_good.wsgi
	<Directory /home/lct/user.server/recommend/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/rec.good.error.log
	LogLevel warn
	CustomLog /home/lct/logs/rec.good.access.log combined
</VirtualHost>
```

```shell
sudo vim /etc/apache2/apache2.conf
# add "ServerName DomainName" on the top
# DomainName: like "secure.hanjianqiao.cn"
sudo vim /etc/apache2/ports.conf
# port listen 14000
mkdir /home/lct/logs
chmod 777 /home/lct/logs
```

Configure folder

```shell
sudo groupadd varwwwusers
sudo chgrp -R varwwwusers /home/lct/user.server/recommend
sudo adduser www-data varwwwusers
sudo chmod -R 770 /home/lct/user.server/recommend/
sudo usermod -a -G varwwwusers lct
git config core.filemode false
```

Restart Apache

```shell
sudo apache2ctl restart
```

#### Nginx

```shell
sudo vim /etc/nginx/conf.d/nginx_rec_good.conf

# start nginx
sudo nginx

# reload config
sudo nginx -s reload 
```

File:

```
# nginx_rec_good.conf
server {
    listen          7010;
    server_name     shop.vsusvip.com;
    location / {
        proxy_pass http://localhost:14000;
    }
}
```



### User server

### Apache

```shell
sudo vim /etc/apache2/sites-enabled/000-default.conf
```

add following to the file

```
# App server
<VirtualHost *:15000>
	DocumentRoot /home/lct/user.server/app
	WSGIScriptAlias / /home/lct/user.server/app/apache_app.wsgi
	<Directory /home/lct/user.server/app/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/app.error.log
	LogLevel warn
	CustomLog /home/lct/logs/app.access.log combined
</VirtualHost>

# Bill server
<VirtualHost *:15001>
	DocumentRoot /home/lct/user.server/bill
	WSGIScriptAlias / /home/lct/user.server/bill/apache_bill.wsgi
	<Directory /home/lct/user.server/bill/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/bill.error.log
	LogLevel warn
	CustomLog /home/lct/logs/bill.access.log combined
</VirtualHost>

# Charger server
<VirtualHost *:15002>
	DocumentRoot /home/lct/user.server/charger/
	WSGIScriptAlias / /home/lct/user.server/charger/apache_charger.wsgi
	<Directory /home/lct/user.server/charger/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/charger.error.log
	LogLevel warn
	CustomLog /home/lct/logs/charger.access.log combined
</VirtualHost>

# User get server
<VirtualHost *:15003>
	DocumentRoot /home/lct/user.server/
	WSGIScriptAlias / /home/lct/user.server/apache_user_get.wsgi
	<Directory /home/lct/user.server/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/user.get.error.log
	LogLevel warn
	CustomLog /home/lct/logs/user.get.access.log combined
</VirtualHost>

# Message server
<VirtualHost *:15004>
	DocumentRoot /home/lct/user.server/message/
	WSGIScriptAlias / /home/lct/user.server/message/apache_message.wsgi
	<Directory /home/lct/user.server/message/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/message.error.log
	LogLevel warn
	CustomLog /home/lct/logs/message.access.log combined
</VirtualHost>

# User server
<VirtualHost *:15005>
	DocumentRoot /home/lct/user.server/user/
	WSGIScriptAlias / /home/lct/user.server/user/apache_user.wsgi
	<Directory /home/lct/user.server/user/>
		Require all granted
		Require host ip
	</Directory>
	ErrorLog /home/lct/logs/user.error.log
	LogLevel warn
	CustomLog /home/lct/logs/user.access.log combined
</VirtualHost>
```

```shell
sudo vim /etc/apache2/apache2.conf
# add "ServerName DomainName" on the top
# DomainName: like "secure.hanjianqiao.cn"
sudo vim /etc/apache2/ports.conf
# port listen 15000 to 15005
mkdir /home/lct/logs
chmod 777 /home/lct/logs
```

Configure folder

```shell
sudo groupadd varwwwusers
sudo chgrp -R varwwwusers /home/lct/user.server/
sudo adduser www-data varwwwusers
sudo chmod -R 770 /home/lct/user.server/
sudo usermod -a -G varwwwusers lct
git config core.filemode false
```

Restart Apache

```shell
sudo apache2ctl restart
```

#### Nginx

```shell
sudo vim /etc/nginx/conf.d/nginx_app.conf
sudo vim /etc/nginx/conf.d/nginx_bill.conf
sudo vim /etc/nginx/conf.d/nginx_charge.conf
sudo vim /etc/nginx/conf.d/nginx_user_get.conf
sudo vim /etc/nginx/conf.d/nginx_message.conf
sudo vim /etc/nginx/conf.d/nginx_user.conf

# OR YOU CAN DO IT IN A SINGLE FILE: nginx_all_user.conf
# sudo vim /etc/nginx/conf.d/nginx_all_user.conf

# start nginx
sudo nginx

# reload config
sudo nginx -s reload
```

File:

```
# nginx_app.conf
server {
    listen          13420;
    server_name     user.vsusvip.com;
    location / {
        proxy_pass http://localhost:15000;
    }
}

# nginx_bill.conf
server {
    listen          40000;
    server_name     user.vsusvip.com;
    location / {
        proxy_pass http://localhost:15001;
    }
}

# nginx_charge.conf
server {
    listen          2100;
    server_name     user.vsusvip.com;
    ssl on;
    ssl_certificate   /home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.pem;
    ssl_certificate_key  /home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.key;
    ssl_session_timeout 5m;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    location / {
        proxy_pass http://localhost:15002;
    }
}

# nginx_user_get.conf
server {
    listen          10000;
    server_name     user.vsusvip.com;
    ssl on;
    ssl_certificate   /home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.pem;
    ssl_certificate_key  /home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.key;
    ssl_session_timeout 5m;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    location / {
        proxy_pass http://localhost:15003;
    }
}

# nginx_message.conf
server {
    listen          30000;
    server_name     user.vsusvip.com;
    location / {
        proxy_pass http://localhost:15004;
    }
}

# nginx_user.conf
server {
    listen          7009;
    server_name     user.vsusvip.com;
    ssl on;
    ssl_certificate   /home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.pem;
    ssl_certificate_key  /home/lct/user.server/sslcrts/user.vsusvip.com/user.vsusvip.com.key;
    ssl_session_timeout 5m;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    location / {
        proxy_pass http://localhost:15005;
    }
}
```

