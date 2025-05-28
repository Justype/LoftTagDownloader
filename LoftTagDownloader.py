#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, requests, time
from bs4 import BeautifulSoup
from urllib import parse
from requests import ReadTimeout, ConnectionError

# region 可设置
tag = ""  # 标签名，如果不填，在命令行内输入

hotMin = 0          # 最低热度
blogMinDate = ""    # 最小时间 YYYY-mm-dd
ignoreTags = []     # 想要去除的标签 ['tag1', 'tag2']  不区分大小写
blogMinLength = 0   # 文章最小长度


isDownloadBlogImg = True    # 是否下载  博客图片
isDownloadLinkImg = True    # 是否下载  外链图片
isDownloadBlogContent = True  # 是否下载  文章
isDownloadBlogWhileItHasImg = False  # 如果博客有图片，是否下载文章
blogImgSize = "原图"    # 下载博客图片的大小 ("缩略图", "小图", "大图", "原图")
isSortByAuthor = False  # 是否按作者分类


# 下载目录 可换成自己想要的,  默认：桌面/Lofter
mainPath = os.path.expanduser("~\\Desktop\\Lofter")
# mainPath = "D:\\Lofter"

# 如果断了可以看 日志，然后修改下面两个继续
requestPosition = 0     # 请求位置      默认 0      每次递增 请求数
requestTime = '0'       # 请求博客的时间      默认 '0'   无法影响请求位置
requestNum = 100        # 每次请求博客的个数
# 如果请求过于频繁，会被断连；如果每次请求过多，正则处理的慢。

isReRequest = True      # DWR请求失败后 是否重新请求
reRequestInterval = 5   # DWR请求失败后 重新请求的秒数

# endregion

# region 不会就别改，折叠起来

while tag == "":
    tag = input("tag：")

imgExtentionPattern = re.compile(r'(\.jpg|\.png|\.gif|\.jpeg)')
ignoreTagsSet = {tag.lower() for tag in ignoreTags}

imgLinksRegexDict = {
    "缩略图" : r'"small":"(.+?)"',
    "小图" : r'"middle":"(.+?)"',
    "大图" : r'"orign":"(.+?)"',
    "原图" : r'"raw":"(.+?)"',
}
imgLinksRegex = imgLinksRegexDict[blogImgSize]

if blogMinDate == "":
    blogMinTime = 0.0
else:
    blogMinTime = time.mktime(time.strptime(blogMinDate + " 00:00:00", "%Y-%m-%d %H:%M:%S"))*1000
# region Methods


def ProcessBadFileName(fileName:str)->str:
    '''
    处理不好的文件名？
    :param fileName:报错的文件名
    :return:可能能打印的文件名
    '''
    return repr(fileName)[1:-1]


def PrintSave(saveInfo:str):
    '''
    打印信息，try UnicodeEncodeError
    :param saveInfo:信息
    '''
    try:
        print(saveInfo)
    except UnicodeEncodeError:
        print(" 该作者名称含有非法的Unicode字符，但是正在下载图片，需要时间，请稍候")


def LogEvent(logType:str, logInfo:str="", isPrintDetail:bool=True):
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


def ValidateFileName(fileName:str)->str:
    '''
    去除非法字符
    :param fileName:文件名
    :return:去除非法字符的文件名
    '''
    rstr = r"[\/\\\:\*\?\"\<\>\|\t\n\r\0]+|[ \.]+$|^[\.]+" # '/ \ : * ? " < > | \t \n \r \0 结尾的空格和. 开头的.
    return re.sub(rstr, "_", fileName)


def GetHeaders(tag:str)->str:
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


def GetPayload(tag:str, requestNum:int, requestPosition:int, requestTime:str)->str:
    '''
    :param tag:tag名
    :param requestNum:每次的请求数
    :param requestPosition:搜索开始位置
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
        "c0-param7=number:" + str(requestPosition) + '\n'           # 当前请求的位置
        "c0-param8=number:" + requestTime + '\n'             # 开始搜索的时间
        "batchId=123456"
    )


def DownloadFile(fullFileName:str, url:str, downloadInfo:str):
    '''
    下载文件
    :param fullFileName:文件名+后缀
    :param url:文件url
    :param downloadInfo:下载的信息
    '''
    if os.path.exists(fullFileName):
        return
    PrintSave(downloadInfo)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
    for i in range(3):
        try:
            with requests.get(url, headers=headers, timeout=8, stream=True) as r, open(fullFileName, 'wb') as f:
                # if r.status_code != 200:
                #     continue
                totalSize = int(r.headers['content-length'])    # 请求文件的大小单位字节B（bytes）
                if totalSize > 1048576:
                    totalSizePrompt = " 共%.2fMB" % (totalSize / 1048576)
                else:
                    totalSizePrompt = " 共%.2fKB" % (totalSize / 1024)
                print(totalSizePrompt, end='\r')
                contentSize = 0     # 已下载的字节大小
                startTime = time.time()    # 请求开始的时间
                lastSize = 0       # 上一秒的下载大小

                # 开始下载每次请求1024字节
                for content in r.iter_content(chunk_size=1024):
                    f.write(content)
                    contentSize += len(content) # 统计以下载大小
                    # 每一秒统计一次下载量
                    time_interval = time.time() - startTime
                    if time_interval > 1:
                        progress = (contentSize / totalSize) * 100  # 计算下载进度
                        speed = (contentSize - lastSize) / time_interval    # 每秒的下载量
                        
                        if speed < 1048576:    # KB级下载速度处理
                            print(totalSizePrompt, " %.2f%% %.2fKB/s" %(progress, speed / 1024), end='    \r')
                        else:   
                            print(totalSizePrompt, " %.2f%% %.2fMB/s" %(progress, speed / 1048576), end='    \r')

                        startTime = time.time()    # 重置开始时间
                        lastSize = contentSize    # 重置以下载大小
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


def ProcessHtmlLinks(html:str, fileName:str, info:str)->str:
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
    counter = 1
    for link in links:
        linkText = link.get_text()
        # a标签内可能无链接
        try:
            linkUrl = link["href"]
        except KeyError:
            continue
        if isDownloadLinkImg:
            # 如果链接指向图片，直接下载
            imgExtention = imgExtentionPattern.search(linkUrl)
            if imgExtention != None:
                linkImgInfo = info + "的外链图片"
                # 可能有的人直接把链接粘到博客中，造成文件名过长
                if len(linkText) > 20:
                    DownloadFile(fileName + "外链图片" + str(counter) + imgExtention.group(1), linkUrl, linkImgInfo)
                    counter += 1
                    continue
                DownloadFile(fileName + ValidateFileName(linkText) + imgExtention.group(1), linkUrl, linkImgInfo)
                continue
        text += linkText + '\n'
        text += linkUrl + '\n'
    return text


def DownloadImgs(fileName:str, imgLinks:str, imgInfo:str):
    '''
    下载图像链接 列表
    :param fileName:想要保存的文件名（不要后缀）
    :param imgLinks:图像链接 列表
    :param imgInfo:图片信息前缀
    '''
    counter = 0
    while imgLinks != []:
        imgLink = imgLinks.pop(0)
        imgExtention = imgExtentionPattern.search(imgLink)
        # 有可能没有 要求的后缀名
        if imgExtention == None:
            continue
        DownloadFile(fileName + '_' + str(counter) + imgExtention.group(1), imgLink, imgInfo + str(counter))
        counter += 1


def ProcessResponseText(text:str)->str:
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
            publishTime = publishTimePattern.search(text).group(1)
            # 小于规定时间，结束
            if int(publishTime) < blogMinTime:
                return None
            # 转换为可读文本
            readablePublishTime = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(float(publishTime)/1000))

            # 获取 tag
            tagsPattern = re.compile(blog + r'\.tag="(.+?)";')
            tags = tagsPattern.search(text).group(1)
            if len(ignoreTagsSet) > 0:
                tagsList = tags.lower().split(',')
                # 如果 tag有交集， 跳过
                if len(ignoreTagsSet.intersection(tagsList)) > 0:
                    continue

            # 获取热度
            hotPattern = re.compile(blog + r'\.hot=([0-9]+);')
            hot = hotPattern.search(text).group(1)
            if int(hot) < hotMin:
                # 热度小于设定值，跳过
                continue

            # 先获取博客信息
            blogInfoPattern = re.compile(blog + r'.blogInfo=(s[0-9]+)')
            blogInfo = blogInfoPattern.search(text).group(1)
            # 再根据博客信息，获取用户名
            blogNickNamePattern = re.compile(blogInfo + r'\.blogNickName="(.+?)"')
            blogNickName = blogNickNamePattern.search(text).group(1)

            blogPageUrlPattern = re.compile(blog + r'\.blogPageUrl="(.+?)"')
            blogPageUrl = blogPageUrlPattern.search(text).group(1)
            # endregion
        # .search 找不到值会返回None，调用其下方法，会报 AttributeError
        except AttributeError:
            continue
            
        # region 可能为空的数据
        # 获取 标题
        titlePattern = re.compile(blog + r'\.title="(.*?)";')
        titleGroup = titlePattern.search(text)
        if titleGroup == None:
            title = ""
        else:
            title = titleGroup.group(1)

        # 获取 内容
        contentPattern = re.compile(blog + r'\.content="(.*?)";', re.S)
        contentGroup = contentPattern.search(text)
        if contentGroup == None:
            content = ""
        else:
            content = contentGroup.group(1)

        # 获取文章的图片链接
        imgListPattern = re.compile(blog + r'\.originPhotoLinks="\[(.*?)\]"')
        imgList = imgListPattern.search(text)
        if imgList != None:
            imgLinksPattern = re.compile(imgLinksRegex)
            imgLinks = imgLinksPattern.findall(imgList.group(1))
            rawImgLinksPattern = re.compile(r'"raw":"(.+?)"')
            rawImgLinks = rawImgLinksPattern.findall(imgList.group(1))
        else:
            imgLinks = []
            rawImgLinks = []
        # endregion

        #region 名称合法化
        legalNickName = ValidateFileName(blogNickName)
        legalTitle = ValidateFileName(title)
        legalTime = ValidateFileName(readablePublishTime)
        info = " 正在保存：作者=" + legalNickName + "\t时间=" + readablePublishTime
        #endregion

        # region 保存数据
        if isSortByAuthor:
            # 作者目录
            authorPath = os.path.join(tagPath, legalNickName)
            CheckPath(authorPath)
            fileName = os.path.join(authorPath, legalNickName + "_" + legalTitle + '_' + legalTime)
        else:
            fileName = os.path.join(tagPath, legalNickName + "_" + legalTitle + '_' + legalTime)
        textFile = fileName + ".txt"

        # 防止 OSError，UnicodeEncodeError 打断下载
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
                    f.writelines(rawImgLinks)
            if isDownloadBlogImg:
                imgInfo = info + "的图片"
                DownloadImgs(fileName, imgLinks, imgInfo)
        except OSError:
            LogEvent("文件名非法", "Url：" + blogPageUrl, False)
            continue
        except UnicodeEncodeError:
            LogEvent("文件内容含非法字符", "Url：" + blogPageUrl, False)
            continue
        # endregion
        
    # 返回最后博客的发布时间
    return publishTime


def CheckPath(path:str):
    '''
    检查目录，如果不存在，创建
    :param path:路径名
    '''
    if not os.path.isdir(path):
        os.makedirs(path)


# endregion


# region 目录操作
tagPath = os.path.join(mainPath, tag)
CheckPath(tagPath)
logFile = os.path.join(tagPath, "log.txt")
# endregion

# 请求的地址
url = "http://www.lofter.com/dwr/call/plaincall/TagBean.search.dwr"
headers = GetHeaders(tag)

try:
    while True:
        try:
            payload = GetPayload(tag, requestNum, requestPosition, requestTime)
            LogEvent("开始请求", "requestPosition= "+str(requestPosition) + ", requestTime= " + requestTime)
            with requests.post(url=url, data=payload, headers=headers) as r:
                r.encoding = "unicode_escape"
                requestPosition += requestNum
                requestTime = ProcessResponseText(r.text)
            if(requestTime == None):
                LogEvent("下载结束")
                break
        except (ConnectionError, TimeoutError, ReadTimeout) as e:
            if isinstance(e, ConnectionError):
                errorType = "连接失败"
            elif isinstance(e, TimeoutError):
                errorType = "连接超时"
            else:
                errorType = "读取超时"

            LogEvent(errorType, "requestPosition= " + str(requestPosition) + ", requestTime= " + requestTime)
            if isReRequest:
                for i in range(int(reRequestInterval), 0, -1):
                    print(" 请求暂停，" + str(i) + "秒后，再次请求", end='\r')
                    time.sleep(1)
            else:
                break

except KeyboardInterrupt:
    LogEvent("下载被打断", "requestPosition= "+str(requestPosition) + ", requestTime= " + requestTime)

print("详细内容请查看日志")

# endregion
