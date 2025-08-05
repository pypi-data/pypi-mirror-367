# BSU

B站字幕批量上传工具

# 使用说明

## 安装

```shell
git clone https://github.com/codingcat1991/bilibili-subtitle-uploader.git
cd bilibili-subtitle-uploader
uv sync
uv build
cd dist
uv pip install bsu-0.1.0-py3-none-any.whl
```

## 使用

```shell
bsu --sessdata xxx --bili_jct xxx --buvid3 xxx --bvid xxx --subtitle-path xxx
```

其中sessdata, bili_jct, buvid3从cookie中获取，bvid从视频链接中获取， subtitle-path为字幕文件路径

**sessdata**

![sessdata](./assets/images/sessdata.png "sessdata")

**bili_jct**

![bili_jct](./assets/images/bili_jct.png "bili_jct")

**buvid3**

![buvid3](./assets/images/bili_jct.png "buvid3")

**bvid**

![bvid](./assets/images/bvid.png "bvid")

# 注意事项

字幕文件命名必须和视频文件名称一样，字幕文件后缀来判断字幕语言，目前支持srt、bcc字幕文件
如字幕文件名：

```text
文件名.en.srt
```

或

```text
文件名.en.bcc
```