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
2. [user_id|password|code] format error
3. user_id already exists
4. code not exist
5. json data format error
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
    qq: string,
    wechat: string,
    taobao: string
}
```