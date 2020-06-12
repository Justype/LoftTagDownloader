# LoftTagDownloader
根据Tag下载Lofter的文章、图片、外链图片

## 需要安装的库
| 库名       | 命令                         |
| ---------- | ---------------------------- |
| `requests` | `pip install requests`       |
| `bs4`      | `pip install beautifulsoup4` |

## 使用方法

修改可设置的部分

```python
#region 可设置
tag = ""  # 标签名

hotMin = 0          # 最低热度
blogMinDate = ""    # 最小时间 YYYY-mm-dd
ignoreTags = [ ]    # 想要去除的标签 ['tag1', 'tag2']  不区分大小写


isDownloadBlogImg = True    # 是否下载  博客图片
isDownloadLinkImg = True    # 是否下载  外链图片
isDownloadBlogContent = True    #是否下载  文章
isDownloadBlogWhileItHasImg = True   #如果博客有图片，是否下载文章
blogMinLength = 0       # 文章最小长度
isSortByAuthor = False  # 是否按作者分类


# 下载目录 可换成自己想要的,  默认：桌面/Lofter
mainPath = os.path.join(os.path.expanduser('~'), "Desktop", "Lofter")
# mainPath = "D:\\Lofter"


# 如果断了可以看 日志，然后修改下面两个继续
i = 0               # 循环变量      默认 0      每次递增 请求数
lastTime = '0'      # 记录时间      默认 '0'
requestsNum = 100   # 每次请求博客的个数
# 如果下图片，可以设置的小一点
# 如果规定了最小时间，建议设置小一点的请求数

#endregion
```

