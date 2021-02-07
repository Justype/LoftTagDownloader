# Lofter Tag 爬虫 教程

1. 请求数据
    - `requests`
2. 分析数据
    - 正则表达式
    - `bs4`
3. 保存数据
4. 额外的功能

## 请求数据

```
         Request（请求想要的内容）
客户端  =========================>  服务器
         Response（返回相应的内容）
客户端  <=========================  服务器
```

### 最常用的请求类型

- `GET`
- `POST`：要提交一些数据

#### GET

```py
import requests

# 向服务器发起 GET 请求
response = requests.get("https://www.lofter.com/tag/%E7%8C%AB")

file = open("result.txt", "w", encoding="utf-8")    # 注意编码

# 使用文件保存 响应 的文本
file.write(response.text)

# 关闭连接
file.close()
response.close()
```

#### POST

```py
import requests

# POST 的地址
url = "https://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr"

# POST 的数据
data = """
callCount=1
scriptSessionId=${scriptSessionId}187
httpSessionId=
c0-scriptName=TagBean
c0-methodName=search
c0-id=0
c0-param0=string:%E7%8C%AB
c0-param1=number:0
c0-param2=string:
c0-param3=string:new
c0-param4=boolean:false
c0-param5=number:0
c0-param6=number:80
c0-param7=number:0
c0-param8=number:0
batchId=255460"""

# 请求标头
headers = {
    "referer" : "https://www.lofter.com/tag/%E7%8C%AB?tab=archive"
}

# 向服务器发起 POST 请求
response = requests.post(url, data, headers=headers)

print(response.headers)

file = open("result.txt", "w", encoding="utf-8")    # 注意编码

# 使用文件保存 响应 的文本
file.write(response.text)

# 关闭连接
file.close()
response.close()
```
