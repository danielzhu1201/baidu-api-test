#coding:utf8
import requests
import json
import sys
import re
from data import data 

space_sep = " "
no_chinese_word_re = u"[^\d\w\u4E00-\u9FA5\u9FA6-\u9FCB]"
some_emoji_code = u"\u141b|\u1597|\u2740|\u30fb|\u1598|\u2665|\u2611"

#data = u"我来测试的"

from aip import AipNlp

data = data[5000:5200]

data = u"帥|科技美学|人物 锤子科技 朱萧木 一个产品经理的自白—在线播放—优酷网，视频高清在线观看"
data = u"大沙漠惊现地中海，储量相当黄河的12%，中亚发展提前进入高速路, 大沙漠惊现地中海，储量相当黄河的12%，中亚发展提前进入高速路, 锤子科技股份有限公司发布会插曲，法国探险家自制飞艇 挑战飞越地中海, 我是中海油“海思韵”艺术团李梦 为自己打call！, 中海油“海思韵”艺术团广场舞《功夫瑜伽》"
print data
args = {
            "APP_ID" : '10867218',#hong81293
            "API_KEY" : '26am6H5pl4RmQmDL6kymlFXb',
            "SECRET_KEY" : '7dKVvQGrSa70Cr2E9GWw53O8t8kgN3z1',}

client = AipNlp(args["APP_ID"], args["API_KEY"], args["SECRET_KEY"])
_replace_sentence = re.sub(
                some_emoji_code,
                space_sep,
                re.sub(
                    no_chinese_word_re,
                    space_sep,
                    data
                    )
                )
print _replace_sentence

json_result = client.lexer(_replace_sentence.encode("utf8"))
print json.dumps(json_result, indent=4, ensure_ascii = False)

