#coding:utf8
import time
import random

from aip import AipSpeech
from aip import AipNlp

import logging

def get_baidu_nlp_client(api=None):
    random.seed(time.time() * 1000)
    if api == "voice_to_sentence":
        args = random.choice([
            {
            "APP_ID" : '10846751',
            "API_KEY" : 'fQVRC7FP989ZgzCBFt87Ul9p',
            "SECRET_KEY" : 'QWUCl8wlTC07DFoCIVK5MIYtqY1QCnkG',},
            ])
        client = AipSpeech(args["APP_ID"], args["API_KEY"], args["SECRET_KEY"])
    elif api in [None,"sentence_to_words"]:
        args = random.choice([
            {
            "APP_ID" : '10880420',#jinghui
            "API_KEY" : 'flSG6dAlW15sNd7YGbFUWyMp',
            "SECRET_KEY" : 'KUMAgRFZsGZNLG7e2c3aSUP2joh4cEuq',},
            {
            "APP_ID" : '10854280',#chu8129,2kw
            "API_KEY" : 'iG4gHufA41LGTo18pokuPXPP',
            "SECRET_KEY" : 'i5tEDTYV5IddsUZKG7poomKbbDXajuaQ',},
            {
            "APP_ID" : '10864948',#20chu 1.5kw
            "API_KEY" : 'yx9Zc8Rt1LV3eEEq4h6ZGi4M',
            "SECRET_KEY" : 'n9cI3zkVtkBaURsPjg06iFjGt3MNbGp0',},
            {
            "APP_ID" : '10867218',#hong81293i，2kw
            "API_KEY" : '26am6H5pl4RmQmDL6kymlFXb',
            "SECRET_KEY" : '7dKVvQGrSa70Cr2E9GWw53O8t8kgN3z1',},
            {
             "APP_ID" : '10914857',#yabiao
             "API_KEY" : 'ChjaFZzXKLbWK2m3qU7IeIsz',
             "SECRET_KEY" : '1c8GEoyt2vKMplM0Ykk6Y46GkIswKGhU',},
            ])
            #{
            #"APP_ID" : '10874447',#mingwei
            #"API_KEY" : 'qameOwB7cnK9ZwiUnlZ5izvZ',
            #"SECRET_KEY" : 'Kc2mBGyZeYAINGLAMVObPz6GbifBEjBV',},
        logging.debug("args:%s"%args)
        client = AipNlp(args["APP_ID"], args["API_KEY"], args["SECRET_KEY"])

    if "client" in locals():
        return client
