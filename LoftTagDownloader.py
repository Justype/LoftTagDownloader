import os
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib import parse
from requests import ReadTimeout, ConnectionError

# region 可设置
tag = ""  # 标签名，如果不填，在命令行内输入

hotMin = 0          # 最低热度
blogMinDate = ""    # 最小时间 YYYY-mm-dd
ignoreTags = []    # 想要去除的标签 ['tag1', 'tag2']  不区分大小写


isDownloadBlogImg = True    # 是否下载  博客图片
isDownloadLinkImg = True    # 是否下载  外链图片
isDownloadBlogContent = True  # 是否下载  文章
isDownloadBlogWhileItHasImg = False  # 如果博客有图片，是否下载文章
blogMinLength = 0       # 文章最小长度
isSortByAuthor = False  # 是否按作者分类


# 下载目录 可换成自己想要的,  默认：桌面/Lofter
mainPath = os.path.join(os.path.expanduser('~'), "Desktop", "Lofter")
# mainPath = "D:\\Lofter"

# 如果断了可以看 日志，然后修改下面两个继续
requestPosition = 0     # 请求位置      默认 0      每次递增 请求数
requestTime = '0'       # 请求博客的时间      默认 '0'
requestNum = 100        # 每次请求博客的个数
# 如果请求过于频繁，会被断连；如果每次请求过多，正则处理的慢。
isPrintEverySave = True    # 是否打印每次的保存信息


# endregion

# region 不会就别改，折叠起来

while tag == "":
    tag = input("tag：")

imgPattern = re.compile(r'(\.jpg|\.png|\.gif|\.jpeg)')
ignoreTagsSet = {tag.lower() for tag in ignoreTags}

if blogMinDate == "":
    blogMinTime = 0.0
else:
    blogMinTime = time.mktime(time.strptime(blogMinDate + " 00:00:00", "%Y-%m-%d %H:%M:%S"))*1000
# region Methods


def ProcessBadFileName(fileName):
    return repr(fileName)[1:-1]


def PrintSave(info):
    '''
    打印信息，try UnicodeEncodeError
    :param info:信息
    '''
    if isPrintEverySave:
        try:
            print(info)
        except UnicodeEncodeError:
            print("该作者名称含有非法的Unicode字符，但是正在下载图片，需要时间，请稍候")


def LogEvent(logType, logInfo="", isPrintDetail=True):
    '''
    记录日志，保存到 ./tag/log.txt 下
    :param logType:日志类型
    :param logInfo:日志内容
    :param isPrintDetail:是否打印详细信息
    '''
    text = "【" + logType + "】" + logInfo
    if isPrintDetail:
        print(text)
    else:
        print("【" + logType + "】  详细信息请看日志")
    with open(logFile, 'a+', encoding='utf-8') as f:
        f.write(text + '\n')
        f.close


def ValidateFileName(fileName):
    '''
    去除非法字符
    :param fileName:文件名
    :return:去除非法字符的文件名
    '''
    rstr = r"[\/\\\:\*\?\"\<\>\|\t\n\r\0]+|[ \.]+$|^[\.]+" # '/ \ : * ? " < > | \t \n \r \0 结尾的空格和. 开头的.
    return re.sub(rstr, "_", fileName)


def GetHeaders(tag):
    '''
    :param tag:tag名
    :return:请求需要的 Headers
    '''
    return {
        "Accept": '*/*',
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "325",
        "Content-Type": "text/plain",
        "Host": "www.lofter.com",
        "Origin": "http://www.lofter.com",
        "Referer": "http://www.lofter.com/tag/%s?tab=archive" % parse.quote(tag),
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    }


def GetPayload(tag, start, requestTime):
    '''
    :param tag:tag名
    :param start:搜索开始位置
    :param requestTime:最后一个的时间
    :return:请求需要的payload
    '''
    return (
        "callCount=1\n"
        "scriptSessionId=${scriptSessionId}187\n"
        "httpSessionId:\n"
        "c0-scriptName=TagBean\n"
        "c0-methodName=search\n"
        "c0-id=0\n"
        "c0-param0=string:" + parse.quote(tag) + '\n'     # 请求的标签
        "c0-param1=number:0\n"
        "c0-param2=string:\n"
        "c0-param3=string:new\n"
        "c0-param4=boolean:false\n"
        "c0-param5=number:0\n"
        "c0-param6=number:" + str(requestNum) + '\n'     # 每次请求的个数
        "c0-param7=number:" + str(start) + '\n'           # 当前请求的位置
        "c0-param8=number:" + requestTime + '\n'             # 开始搜索的时间
        "batchId=123456"
    )


def DownloadFile(fullFileName, url):
    '''
    下载文件
    :param fullFileName:文件名+后缀
    :url:文件url
    '''
    if os.path.exists(fullFileName):
        return
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
    for i in range(3):
        try:
            fileResponse = requests.get(url, headers=headers, timeout=20)
            if fileResponse.status_code == 200:
                with open(fullFileName, 'wb') as f:
                    f.write(fileResponse.content)
                    f.close()
                # 下载完成退出函数
                return
        except (ConnectionError, ReadTimeout, TimeoutError) as e:
            # 写文本的时候可能会出现异常，可能是文件名的问题，如果出现，请提交issue
            try:
                if i == 2:
                    LogEvent("文件下载失败", "\n目标文件:" + fullFileName + "\nUrl:" + url, False)
            except UnicodeEncodeError:
                LogEvent("文件下载失败", "\n目标文件:" + ProcessBadFileName(fullFileName) + "\nUrl:" + url, False)
                # 实在不行，使用下面的一行，只log Url
                # LogEvent("文件下载失败"+ str(i), "Url:" + url)


def ProcessHtmlLinks(html, fileName, info):
    '''
    下载图像链接，返回所有非图片链接
    如果不下载图片链接，返回所有链接
    :param html:HTML文本
    :param fileName:想要保存的文件名（不要后缀）
    :param info:作者和时间信息
    :return:所有链接
    '''
    links = BeautifulSoup(html, "html.parser").find_all("a")
    text = "\n=====================\n"
    for link in links:
        linkText = link.get_text()
        # a标签内可能无链接
        try:
            linkUrl = link["href"]
        except KeyError:
            continue
        if isDownloadLinkImg:
            # 如果链接指向图片，直接下载
            imgExtencion = imgPattern.findall(linkUrl)
            if imgExtencion != []:
                PrintSave(info + "的外链图片")
                DownloadFile(fileName + ValidateFileName(linkText) + imgExtencion[0], linkUrl)
                continue
        text += linkText + '\n'
        text += linkUrl + '\n'
    return text


def DownloadImgs(fileName, imgLinks):
    '''
    下载图像链接 列表
    :param fileName:想要保存的文件名（不要后缀）
    :param imgLinks:图像链接 列表
    '''
    counter = 0
    while imgLinks != []:
        imgLink = imgLinks.pop(0)
        imgExtencion = imgPattern.findall(imgLink)
        # 有可能没有 要求的后缀名
        if imgExtencion == []:
            continue
        DownloadFile(fileName + '_' + str(counter) + imgExtencion[0], imgLink)
        counter += 1


def ProcessResponseText(text):
    '''
    处理返回的文本
    :param text:Response文本
    :return:最后博客的发布时间
    '''
    # 通过 btextPageUrl 找到文本对象
    blogPattern = re.compile(r'(s[0-9]+)\.blogPageUrl')
    blogs = blogPattern.findall(text)
    # blogs为空则跑完了
    if blogs == []:
        return None
    for blog in blogs:
        try:
            # region 不可能为空的数据
            # 获取 发布时间
            publishTimePattern = re.compile(blog + r'\.publishTime=([0-9]+);')
            publishTime = publishTimePattern.findall(text)[0]
            # 小于规定时间，结束
            if int(publishTime) < blogMinTime:
                return None
            # 转换为可读文本
            readablePublishTime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(float(publishTime)/1000))

            # 获取 tag
            tagsPattern = re.compile(blog + r'\.tag="(.*?)";')
            tags = tagsPattern.findall(text)[0]
            if len(ignoreTagsSet) > 0:
                tagsList = tags.lower().split(',')
                # 如果 tag有交集， 跳过
                if len(ignoreTagsSet.intersection(tagsList)) > 0:
                    continue

            # 获取热度
            hotPattern = re.compile(blog + r'\.hot=([0-9]+);')
            hot = hotPattern.findall(text)[0]
            if int(hot) < hotMin:
                # 热度小于设定值，跳过
                continue

            # 先获取博客id
            blogIdPattern = re.compile(blog + r'\.blogId=([0-9]+);')
            blogId = blogIdPattern.findall(text)[0]
            # 再根据博客id，获取用户名
            blogNickNamePattern = re.compile(blogId + r'.*?blogNickName="(.*?)"')
            blogNickName = blogNickNamePattern.findall(text)[0]

            blogPageUrlPattern = re.compile(blog + r'\.blogPageUrl="(.*?)"')
            blogPageUrl = blogPageUrlPattern.findall(text)[0]
            # endregion
        except IndexError:
            continue
            
        # region 可能为空的数据
        # 获取 标题
        titlePattern = re.compile(blog + r'\.title="(.*?)";')
        title = titlePattern.findall(text)
        if(title):
            title = title[0]
        else:
            title = ""

        # 获取 内容
        contentPattern = re.compile(blog + r'\.content="(.*?)";', re.S)
        content = contentPattern.findall(text)
        if(content):
            content = content[0]
        else:
            content = ""

        # 获取文章的图片链接
        imgListPattern = re.compile(blog + r'\.originPhotoLinks="\[(.*?)\]"')
        imgList = imgListPattern.findall(text)
        if(imgList):
            imgLinksPattern = re.compile(r'"orign":"(.*?)"')
            imgLinks = imgLinksPattern.findall(imgList[0])
        else:
            imgLinks = []
        # endregion

        #region 名称合法化
        legalNickName = ValidateFileName(blogNickName)
        legalTitle = ValidateFileName(title)
        legalTime = ValidateFileName(readablePublishTime)
        info = "正在保存：作者=" + legalNickName + "\t时间=" + readablePublishTime
        #endregion

        # region 保存数据
        if isSortByAuthor:
            # 作者目录
            authorPath = os.path.join(tagPath, legalNickName)
            ChechPath(authorPath)
            fileName = os.path.join(authorPath, legalNickName + "_" + legalTitle + '_' + legalTime)
        else:
            fileName = os.path.join(tagPath, legalNickName + "_" + legalTitle + '_' + legalTime)
        textFile = fileName + ".txt"

        try:
            contentText = BeautifulSoup(content, "html.parser").get_text()
            contentLinks = ProcessHtmlLinks(content, fileName, info)
            #  是否下载博客               长度大于要求                          博客有图片，是否下载           图片为空，下载文章       文件是否不存在
            if isDownloadBlogContent and len(contentText) > blogMinLength and (isDownloadBlogWhileItHasImg or imgLinks == []) and not os.path.exists(textFile):
                PrintSave(info + "的文章")
                with open(textFile, "w", encoding="utf-8", errors="ignore") as f:
                    f.write("标题：" + title + '\n')
                    f.write("昵称：" + blogNickName + '\n')
                    f.write("发布时间：" + readablePublishTime + '\n')
                    f.write("热度：" + hot + '\n')
                    f.write("tag：" + tags + '\n')
                    f.write("Url：" + blogPageUrl + '\n')
                    f.write("内容：\n" + contentText + contentLinks + '\n')
                    f.write("文章图像链接：\n")
                    f.writelines(imgLinks)
                    f.close()
            if isDownloadBlogImg:
                PrintSave(info + "的图片")
                DownloadImgs(fileName, imgLinks)
        except OSError:
            LogEvent("文件名非法", "Url：" + blogPageUrl, False)
            continue
        # endregion
        
    # 返回最后博客的发布时间
    return publishTime


def ChechPath(path):
    '''
    检查目录，如果不存在，创建
    :param path:路径名
    '''
    if not os.path.isdir(path):
        os.makedirs(path)


# endregion


# region 目录操作
tagPath = os.path.join(mainPath, tag)
ChechPath(tagPath)
logFile = os.path.join(tagPath, "log.txt")
# endregion

# 请求的地址
url = "http://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr"
headers = GetHeaders(tag)

try:
    while True:
        payload = GetPayload(tag, requestPosition, requestTime)
        response = requests.post(url=url, data=payload, headers=headers)
        response.encoding = "unicode_escape"
        LogEvent("开始请求", "requestPosition= "+str(requestPosition) + ", requestTime= " + requestTime)
        requestPosition += requestNum
        requestTime = ProcessResponseText(response.text)
        if(requestTime == None):
            LogEvent("下载结束")
            break
except ConnectionError:
    LogEvent("连接失败", "requestPosition= "+str(requestPosition) + ", requestTime= " + requestTime)
except TimeoutError:
    LogEvent("连接超时", "requestPosition= "+str(requestPosition) + ", requestTime= " + requestTime)
except ReadTimeout:
    LogEvent("读取超时", "requestPosition= "+str(requestPosition) + ", requestTime= " + requestTime)
finally:
    print("详细内容请查看日志")

# endregion
