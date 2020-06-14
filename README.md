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

① 找到日志`log.txt`，复制最后一次的`requestPosition`，`requestTime`

```
【开始请求】requestPosition= 0, requestTime= 0
【连接超时】requestPosition= 100, requestTime= 1513515723233
```

或者直接复制命令行内的两个值

② 然后粘贴到 `LoftTagDownloader.py` 内，如下：

```python
# 如果断了可以看 日志，然后修改下面两个继续
requestPosition = 100     # 请求位置      默认 0      每次递增 请求数
requestTime = '1513515723233'       # 请求博客的时间      默认 '0'
requestNum = 100        # 每次请求博客的个数
# 如果请求过于频繁，会被断连；如果每次请求过多，正则处理的慢。
```

③ 再次运行相同的tag

## 其他问题

1. 重新开始跑同一个Tag，会不会再次下载已经下过的？
    - 不会。识别到文件存在，会自己跳过。
2. 为啥文章中的外链显示不全？
    - 如果下载了外链图片，该外链不会添加到文章中。
3. 提示`【文件下载失败】`怎么办？
    - 如果大面积出现说明是网络问题，请稍等一会儿，重新开始下载；
    - 或找到`log.txt`下对应的Url，自行下载对应的图片；
4. 提示`【文件名非法】`怎么办？
    - ！只能找到`log.txt`下对应的Url，自行下载博客对应的内容；
    - 因为我写的重命名正则无法解决所有的非法命名，有些文件名就是有`\x07`等奇怪的符号、还有标题内的Emoji，没办法命名为文件。
    - 如果你有解决办法，请提交PullRequest。（我用于重命名文件的函数名：`ValidateFileName`）

如果还有其他问题，请提交issue

## 大家觉得喜欢，请Star本项目

使用爬虫的时候，建议给`python.exe`添加限速，以免影响他人正常用网
