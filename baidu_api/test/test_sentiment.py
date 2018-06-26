#coding:utf8
import json
import requests

api = "http://localhost:7228/api/v1/sentiment"
data = "《猫和老鼠》很好看,湛江市科技美学|人物 锤子科技 朱萧木 一个产品经理的自白—在线播放—优酷网，视频高清在线观看"
print data.decode('utf8').encode('gbk')
print json.dumps(json.loads(requests.post(api, data={"text":data}).content), ensure_ascii=False, indent=4)
