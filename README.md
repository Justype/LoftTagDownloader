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
# 如果请求过于频繁，会被断连
```

③ 再次运行相同的tag

## 其他问题

1. 程序运行半天，命令行为什么只有`requestPosition= 0, requestTime= 0` ？
    - 现在最新版本已添加`isPrintEverySave = True`，即打印所有保存信息；
    - 如果不想要详细信息请设置为`False`。
2. 提示`【下载外链图片失败】`怎么办？
    - 找到`log.txt`下对应的Url，自行下载对应的图片；
    - 或者重新开始（有可能该外链图片已经被删了）。
3. 重新开始跑同一个Tag，会不会再次下载已经下过的？
    - 不会。识别到文件存在，会自己跳过。
4. 为啥文章中的外链显示不全？
    - 如果下载了外链图片，该外链不会添加到文章中。

如果还有其他问题，请提交issue

## 大家觉得喜欢，请Star本项目
