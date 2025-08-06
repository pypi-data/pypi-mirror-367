from http.client import responses

# netease_encode_api

网易云weapi解码和封装。

## 安装

1. 请下载带有 pip 包安装器的 Python, 并将 Python 添加到 PATH。
2. 打开命令行输入 `pip install netease_encode_api`
3. 在 Python 代码内引用: `from netease_encode_api import EncodeSession`

## 使用

在 1.2.0+ 版本, `EncodeSession` 类已经成为了 `requests.Session` 的子类。
在不需要解码时, 请按照 `request.Session` 的使用方式正常使用。
在需要解码时, 请使用 `EncodeSession.encoded_post(url, data)`。

## 示例

```python
from netease_encode_api import EncodeSession
es = EncodeSession()
# 加密获取歌曲下载链接
url = "https://music.163.com/weapi/song/enhance/player/url/v1"
data = {"ids":"[1462389992]",
        "level":"exhigh",
        "encodeType":"mp3"}
responses = es.encoded_post(url, data)
download_url = responses["data"][0]["url"]
download_responses = es.get(download_url)
with open(test.mp3, "wb") as f: f.write(download_responses.content)

```