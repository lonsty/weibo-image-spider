# Weibo Image Spider

微博图片爬虫，极速下载、高清原图、多种命令、简单实用。

### 特点：

- [x] 极速下载：多线程异步下载，可以根据需要设置线程数
- [x] 异常重试：只要重试次数足够多，就没有下载不下来的图片 \(^o^)/！
- [x] 增量下载：用户有新的上传，再跑一遍程序就行了 O(∩_∩)O 嗯！
- [x] 高清原图：默认下载高清原图，可以使用参数`--thumbnail`下载缩略图（宽最大690px）

### 环境：

- `python3.6` 及以上

# 快速使用

## 1. 克隆项目到本地

```sh
$ git clone https://github.com/lonsty/weibo-image-spider.git
```

## 2. 安装依赖包

```sh
$ cd weibo-image-spider
$ pip3 install -r requirements.txt
```

## 3. 快速使用

下载用户昵称为 `nickname` 的最新 2000（默认） 张图片到路径 `dest` 下：

```sh
$ python3 main.py -u <nickname> -d <dest>
```

运行截图

![screenshot_01.png](screenshots/03.png)

爬取结果

![screenshot_02.png](screenshots/02.png)

# 使用帮助

### 常用命令

1. 部分图片**下载失败**或有**更新**，再执行相同的命令，对失败或新增的图片进行下载

```sh
$ python3 main.py -u <nickname> -d <dest>
```

### 查看所有命令

```
$ python3 main.py --help

Usage: main.py [OPTIONS]

  A Weibo image spider, visit https://github.com/lonsty/weibo-image-spider.

Options:
  -u, --nickname TEXT        Nickname
  -d, --destination TEXT     Directory to save images  [default:
                             weibo_images/]

  -o, --overwrite            Overwrite existing files  [default: False]
  -t, --thumbnail            Download thumbnails with a maximum width of 690px
                             [default: False]

  -n, --max-images INTEGER   Maximum number of images to download  [default:
                             2000]

  -p, --max-pages INTEGER    Maximum number of pages to download  [default:
                             20]

  -w, --max-workers INTEGER  Maximum thread workers  [default: 15]
  -P, --proxies TEXT         Use proxies to access websites. Example:
                             '{"http": "user:passwd@www.example.com:port",
                             "https": "user:passwd@www.example.com:port"}'

  --help                     Show this message and exit.
```

# 更新历史

- ## Version 0.1.0a (2020-03-29)

    主要功能：
    
    - 极速下载：多线程异步下载，可以根据需要设置线程数
    - 异常重试：只要重试次数足够多，就没有下载不下来的图片 \(^o^)/
    - 增量下载：设计师/用户有新的上传，再跑一遍程序就行了 O(∩_∩)O 嗯！
    - 支持代理：可以配置使用代理

# LICENSE

此项目使用 [MIT](LICENSE) 开源协议

**注意**：使用此工具下载的所有内容，版权归原作者所有，请谨慎使用！
