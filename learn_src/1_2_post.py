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