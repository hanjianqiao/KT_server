# Set up Nginx(Ubuntu 16.04 LTS 64)

```bash
wget http://nginx.org/keys/nginx_signing.key
sudo apt-key add nginx_signing.key
sudo vim /etc/apt/sources.list
# add following to the end of file
deb http://nginx.org/packages/ubuntu/ xenial nginx
deb-src http://nginx.org/packages/ubuntu/ xenial nginx
#
sudo apt update
sudo apt install nginx
sudo vim /etc/nginx/conf.d/user_server.conf
#new file content
server {
    listen          10000 ssl;
    server_name     user.vsusvip.com;
    ssl on;
    ssl_certificate   /home/lct/user.server/sslcrts/2_user.vsusvip.com.crt;
    ssl_certificate_key  /home/lct/user.server/sslcrts/3_user.vsusvip.com.key;
    ssl_session_timeout 5m;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    location / {
        proxy_pass http://localhost:13000;
    }
}

server {
    listen          10000 ssl;
    server_name     user.hanjianqiao.cn;
    ssl on;
    ssl_certificate   /home/lct/user.server/sslcrts/2_user.hanjianqiao.cn.crt;
    ssl_certificate_key  /home/lct/user.server/sslcrts/3_user.hanjianqiao.cn.key;
    ssl_session_timeout 5m;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    location / {
        proxy_pass http://localhost:13000;
    }
}
#

# start nginx
sudo nginx

# reload config
sudo nginx -s reloadd 

```

