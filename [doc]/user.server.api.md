# FlaskServer API Document

##### SF-Zhou
##### 2016/12/04 V1.00

<!-- $theme: gaia -->

---

### `/register [POST]`

```json
{
    user_id: string[11 digits],
    password: string[6-20 digits or letters],
    code: string[6 digits],
    email: string[normal email string],
    qq: string,
    wechat: string,
    taobao: string
}
```

`password`: md5(raw_password)

---

### `/register [RESPONSE]`

```json
{
    status: [ok|failed],
    message: string
}
```

`message`:

```
1. register ok
2. [user_id|password|code|email] format error
3. user_id already exists
4. email already exists
5. code not exist
6. json data format error
```

---

### `/login [POST]`

```json
{
    user_id: string[11 digits],
    password: string[6-20 digits or letters]
}
```

`password`: md5(raw_password)

---

### `/login [RESPONSE]`:

```json
{
    status: [ok|failed],
    message: string
}
```

`message`:

```
1. login ok
2. [user_id|password] format error
3. user_id not exist
4. password not match
5. json data format error
```

---

### `/query [POST]`

```json
{
    user_id: string[11 digits],
    password: string[6-20 digits or letters]
}
```

`password`: md5(raw_password)

---

### `/query [RESPONSE]`


```json
{
    status: [ok|failed],
    message: string,
    data: user_info_data if status is ok
}
```

`message`:

```
1. login ok
2. [user_id|password] format error
3. user_id not exist
4. password not match
5. json data format error
```

---

### `/query [RESPONSE]`

`user_info_data`:

```
{
    user_id: string[11 digits],
    inviter: string[11 digits],
    code: string[6 digits],
    email: string,
    qq: string,
    wechat: string,
    taobao: string
}
```

---

### `Database Demo`

![](http://zhijia-10060660.file.myqcloud.com/avatar/20161205132522_893.png)

1. the `inviter` is the inviter of a user
2. the `code` is the code of a user
3. if B use the A's code, then A is the inviter of B

`Test Code`

```
curl -H "Content-Type: application/json" -X POST\
-d '{"user_id":"15913101318","password":"123456","code":"666666", "email":"1@2"}'\
http://127.0.0.1:5000/login
```

---

### `Deploy`

1. `install Apache & mod_wsgi`

```sh
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
```

2. `modify Apache config file`

```sh
sudo vim /etc/apache2/sites-enabled/000-default.conf
# config file detail in next slide
```

3. `Start Apache Server`

```sh
sudo apache2ctl restart
```

---

### `Deploy`

```
<VirtualHost *:80>
    DocumentRoot /home/ubuntu/user.server/
    WSGIScriptAlias / /home/ubuntu/user.server/start.wsgi
    SSLEngine on
    SSLCertificateFile "/home/ubuntu/user.server/server.cert"
    SSLCertificateKeyFile "/home/ubuntu/user.server/server.key"
<Directory /home/ubuntu/user.server/>
    <Files start.wsgi>
        Require all granted
        Require host ip
    </Files>
</Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```