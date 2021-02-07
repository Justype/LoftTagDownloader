import requests

# 向服务器发起 GET 请求
response = requests.get("https://www.lofter.com/tag/%E7%8C%AB")

file = open("result.txt", "w", encoding="utf-8")    # 注意编码

# 使用文件保存 响应 的文本
file.write(response.text)

# 关闭连接
file.close()
response.close()