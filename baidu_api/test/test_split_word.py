#coding:utf8
import json
import requests

api = "http://localhost:7228/api/v1/split_sentence_single"
data = "《猫和老鼠》很好看,湛江市科技美学|人物 锤子科技 朱萧木 一个产品经理的自白—在线播放—优酷网，视频高清在线观看"
data = "大沙漠惊现地中海，储量相当黄河的12%，中亚发展提前进入高速路, 大沙漠惊现地中海，储量相当黄河的12%，中亚发展提前进入高速路, 锤子科技股份有限公司发布会插曲，法国探险家自制飞艇 挑战飞越地中海, 我是中海油“海思韵”艺术团李梦 为自己打call！, 中海油“海思韵”艺术团广场舞《功夫瑜伽》"
print json.dumps(json.loads(requests.post(api, data={"sentence":data}).content), ensure_ascii=False, indent=4)
