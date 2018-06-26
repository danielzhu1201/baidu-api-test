#coding:utf8

from aip import AipSpeech
from aip import AipNlp
from aip import AipOcr


accounts = (
            {"APP_ID" : '10880420',#jinghui
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
            {
            "APP_ID" : '10874447',#mingwei
            "API_KEY" : 'qameOwB7cnK9ZwiUnlZ5izvZ',
            "SECRET_KEY" : 'Kc2mBGyZeYAINGLAMVObPz6GbifBEjBV',},
)

def get_baidu_nlp_client(num):
    args = accounts[num]
    client = AipNlp(args["APP_ID"], args["API_KEY"], args["SECRET_KEY"])
    return client




'''
avaliable accounts

{
            {"APP_ID" : '10880420',#jinghui
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
            {
            "APP_ID" : '10874447',#mingwei
            "API_KEY" : 'qameOwB7cnK9ZwiUnlZ5izvZ',
            "SECRET_KEY" : 'Kc2mBGyZeYAINGLAMVObPz6GbifBEjBV',},
}

'''
