# PTCheat

灵感来源于[这篇文章](https://blog.lyc8503.net/post/pt-hack/)，主要流程如下：从 PT 站点下载原始种子文件，向 tracker 服务器请求 peerlist，并将该 peerlist保存到本地。自建一个 tracker 来返回 peerlist。这里在原作者代码的基础上做了些许修改。

## 用法

- `python main.py -G`：生成免费种子
- `python main.py -S`：启动本地 tracker

## 问题

#### 种子文件存放位置

请将种子文件放置在 `main.py` 同目录下的 `torrents` 文件夹中。

#### Tracker 地址

默认地址为 `127.0.0.1:54321`。

- `/announce`：根据种子的 infohash 返回对应的 peer 列表。
- `/announce2`：返回获取到的所有 peer 列表。

#### 存在的风险

与站点的交互全程只有请求peerlist这一个，但是只请求peerlist却不下载还是比较可疑的。最后，风险自负！

# myblog
