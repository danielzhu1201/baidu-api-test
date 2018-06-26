#!/usr/bin/env python
# -*- coding: utf-8 -*-
# qw @ 2018-03-07 15:28:46

import requests


def get_video(data):
    url = 'http://localhost:5555/'
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
    data.append({'source': u'tencent', 'video_id': u'z055962al06', 'video_url': u'https://v.qq.com/x/cover/z3uq0ji0cwvxkd8/z055962al06.html'})
    #data.append({u'source': u'tudou', u'video_id': u'868800556', u'video_url': u'http://new-play.tudou.com/v/868800556.html', u'uper_name': u'\u8427\u4f55\u4e3a\u4f55\u7ed9\u5218\u90a6\u4e3e\u8350\u97e9\u4fe1, \u6700\u540e\u5374\u53c8\u8bf1\u6740\u4e86\u4ed6?_\u571f\u8c46\u89c6\u9891'})
    data.append({u'source': u'aiqiyi', u'video_id': u'12340279509', u'video_url': u'http://www.iqiyi.com/w_19rw205ebd.html#vfrm=8-8-0-1', u'uper_name': u'\u6cd5\u6069\u838e'})
    data.append({'source': u'meipai', 'video_id': u'975809312', 'video_url': u'http://www.meipai.com/media/975809312', 'uper_name': u'\u5468\u672b\u6109\u5feb\uff01\U0001f618\U0001f618\U0001f91f\U0001f91f\U0001f600@\u90ed\u5b50\u82e5\u5168\u56fd\u540e\u63f4\u4f1a @\u7f8e\u62cd\u5c0f\u52a9\u624b'})
    data.append({u'source': u'tencent', u'video_id': u'd0607pmu3x0', u'video_url': u'https://v.qq.com/x/page/d0607pmu3x0.html', u'uper_name': u'\u524d\u7537\u53cb\u662f\u8001\u677f\uff01'})
    data.append({u'source': u'tencent', u'video_id': u'd0607ssqiod', u'video_url': u'https://v.qq.com/x/page/d0607ssqiod.html', u'uper_name': u'\u5b9e\u62cd\u5c31\u9910\u5403\u51fa\u866b\uff0c\u987e\u5ba2\u8981\u6c42\u670d\u52a1\u5458\u5403\u6389\u5c31\u7ed3\u5e10\uff0c\u7ed3\u679c\u5973\u5b50\u771f\u7684\u5403\u4e86\uff01'})
    data.append({u'video_url': u'https://v.qq.com/x/page/s0611r9xirj.html', u'forward_count': None, u'like_count': -1, u'publisher_name': u'\u5927\u8748\u5c0f\u9171', u'id': 463596153, u'category': u'\u7535\u89c6\u5267', u'tags': u'["u6613u8fdeu607a", "u79e6u6851", "u4ebau751fu82e5u5982u521du89c1", "u8650u604b"]', u'comment_count': 60, u'subtitle_status': 0, u'hot_update_date': u'2018-04-02 17:39:06', u'hot': 5864, u'thumbnail_url': u'http://vpic.video.qq.com/66860611/s0611r9xirj_160_90_3.jpg', u'publisher_id': u'd051f175d67c514967d5bd9617482a49', u'update_time': u'2018-03-24 05:49:23', u'video_source': u'tencent', u'play_count': 1746836, u'video_voice_subtitle': u'', u'publisher_avatar_url': u'https://puui.qpic.cn/video_caps_enc/2lR7bG410nZic4tqo3RJbCictERI9L0iaiaFTLicxxtZkwcY5UqjXhuh1tg/0', u'hot_words': u'{}', u'video_id': u's0611r9xirj', u'create_time': u'2018-03-22 00:00:00', u'video_title': u'\u8fd9\u624d\u662f\u300a\u4eba\u751f\u82e5\u5982\u521d\u76f8\u89c1\u300b\u5b8c\u7f8e\u7ed3\u5c40\uff0c\u5403\u7cd6\u592b\u5987\u72c2\u6492\u7cd6\uff01'})
    data.append({"source": "xiguavideo", "video_id": "6507794484661584391", "video_url": "https://www.365yg.com/a6507794484661584391", "uper_name": u"\\u5353\\u522b\\u4f60\\u4e0d\\u7b11"})
    data.append({u'source': u'tencent', u'video_id': u'v1425vxnj6l', u'video_url': u'https://v.qq.com/x/page/v1425vxnj6l.html', u'uper_name': u'\u534e\u54e5\u6076\u641e'})
    for _data in data:
        print "\n\n\n"
        print "request data", _data
        print get_video(_data)
    
    
