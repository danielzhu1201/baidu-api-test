#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2018-03-07 15:28:46

import requests


def get_video(data):
    #url = 'http://172.16.6.55:5555'
    url = "http://localhost:7228/api/v1/video_to_sentence"
    req = requests.post(url,data)
    return req.content

if __name__ == "__main__":
    data = []
    data.append({
       'source':'365yg',
       'video_url' : 'https://m.365yg.com/i6526785198103724551/',
       'uper_id':'4329359793',
       'uper_name':'暴影君',
       'video_title':'夺命五头鲨，5个头的鲨鱼你见过吗',
       'video_id':'6526785198103724551'
        }
    )
    """
    data.append({
       'source':'bilibili',
       'video_url' : 'https://www.bilibili.com/video/av8524854/?from=search&seid=14792893731548268258',
       'uper_id':None,
       'uper_name':None,
       'video_title':None,
       'video_id': "av8524854",
        }
    )
    """
    data.append({
       'source':'youku',
       'video_url' : 'http://v.youku.com/v_show/id_XMTM3NTEzMzkzMg==.html?spm=a2h0j.11185381.listitem_page1.5!5~A&s=2c1e303055f011e5a080',
       'uper_id':None,
       'uper_name':None,
       'video_title':None,
       #'video_id': "XMTM3NTEzMzkzMg==",
        }
    )
    data.append({
       'source':'tencent',
       'video_url' : "https://v.qq.com/x/cover/z3uq0ji0cwvxkd8/z055962al06.html",
       'uper_id':None,
       'uper_name':None,
       'video_title':None,
       'video_id': "z055962al06",
        }
    )
    for _data in data:
        print get_video(_data)
    
    
