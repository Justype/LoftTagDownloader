# LoftTagDownloader
根据Tag下载Lofter的文章、图片、外链图片

## 需要安装的库
| 库名       | 命令                         |
| ---------- | ---------------------------- |
| `requests` | `pip install requests`       |
| `bs4`      | `pip install beautifulsoup4` |

## 使用方法

下载`LoftTagDownloader.py`，修改可设置的部分，直接运行。

| 使用目的                      | 只下长文   | 只下图片 | 图文均下 |
| ----------------------------- | ---------- | -------- | -------- |
| `isDownloadBlogImg`           | `False`    | `True`   | `True`   |
| `isDownloadLinkImg`           | `False`    | `True`   | `True`   |
| `isDownloadBlogContent`       | `True`     | `False`  | `True`   |
| `isDownloadBlogWhileItHasImg` | `False`    | 无所谓   | `True`   |
| `blogMinLength`               | 建议 `200` | 无所谓   | 按需     |

```python
#region 可设置
tag = ""  # 标签名，如果不填，在命令行内输入

hotMin = 0          # 最低热度
blogMinDate = ""    # 最小时间 YYYY-mm-dd
ignoreTags = [ ]    # 想要去除的标签 ['tag1', 'tag2']  不区分大小写

isDownloadBlogImg = False    # 是否下载  博客图片
isDownloadLinkImg = False    # 是否下载  外链图片
isDownloadBlogContent = True    #是否下载  文章
isDownloadBlogWhileItHasImg = True   #如果博客有图片，是否下载文章
blogMinLength = 0       # 文章最小长度
isSortByAuthor = False  # 是否按作者分类
```

## 如果中途被断了

找到日志`log.txt`，将最后一次的`requestPosition`，`requestTime`

```
【开始下载】requestPosition= 0, requestTime= 0
【开始下载】requestPosition= 100, requestTime= 1513515723233
【下载结束】
```

或者直接复制命令行内的两个值，左边是`requestPosition`，右边是`requestTime`

然后复制到 `LoftTagDownloader.py` 内

```python
# 如果断了可以看 日志，然后修改下面两个继续
requestPosition = 0     # 请求位置      默认 0      每次递增 请求数
requestTime = '0'       # 记录时间      默认 '0'
requestNum = 100        # 每次请求博客的个数
# 如果请求过于频繁，会被断连
```

