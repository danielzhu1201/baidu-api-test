#!/usr/bin/env python                                                                                               
# -*- coding: utf-8 -*-
# qw @ 2018-02-23 15:16:30

import os
import re
import sys
import copy
import time
import json
import redis
import random
import logging
import requests
import commands
import traceback
import subprocess
from multiprocessing import Process
from aip import AipSpeech
from aip import AipNlp

from flask import Flask
from flask import request
app = Flask(__name__)

import gevent
import gevent.pool
import gevent.monkey
gevent.monkey.patch_socket()
pool=gevent.pool.Pool(20)

#logging.basicConfig(level=logging.DEBUG)
logging_level = logging.WARN
logging_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
logging.basicConfig(level=logging_level, format=logging_format)
logging.getLogger().setLevel(logging_level)
logging.getLogger('werkzeug').setLevel(logging_level)
logging.getLogger("requests").setLevel(logging_level)
logging.getLogger('urllib3').setLevel(logging_level)

redis_host = "localhost"
redis_port = 6379
redis_db = 14
redis_task_list_name = "wait_download_video_list"
redis_save_video_result = "video_to_sentence_result"
get_video_api = "http://106.75.153.17:5555"
baidu_api_error_try_times = 10

space_sep = " "
sep = "#\t@;`"
sep_replace = ("\s?").join([_sep for _sep in sep])
no_chinese_word_re = u'[^\d\w\u4E00-\u9FA5\u9FA6-\u9FCB\s+\.\!\/:\?《》\-“”_,\$\%\*\(\+\"\'\]\|\[\]\—！，。？、~@#￥%……\&（）【】：<>]'
some_emoji_code = u"\u141b|\u1597|\u2740|\u30fb|\u1598|\u2665|\u2611"

dont_split_pos = set(["nw","n"])
dont_split_ne = set(["per","loc"])

def get_baidu_nlp_client(api):
    random.seed(time.time() * 1000)
    if api == "voice_to_sentence":
        args = random.choice([
            {
            "APP_ID" : '10846751',
            "API_KEY" : 'fQVRC7FP989ZgzCBFt87Ul9p',
            "SECRET_KEY" : 'QWUCl8wlTC07DFoCIVK5MIYtqY1QCnkG',},
            ])
        client = AipSpeech(args["APP_ID"], args["API_KEY"], args["SECRET_KEY"])
    elif api == "sentence_to_words":
        args = random.choice([
            {
            "APP_ID" : '10880420',#jinghui
            "API_KEY" : 'flSG6dAlW15sNd7YGbFUWyMp',
            "SECRET_KEY" : 'KUMAgRFZsGZNLG7e2c3aSUP2joh4cEuq',},
            {
            "APP_ID" : '10854280',#chu8129
            "API_KEY" : 'iG4gHufA41LGTo18pokuPXPP',
            "SECRET_KEY" : 'i5tEDTYV5IddsUZKG7poomKbbDXajuaQ',},
            {
            "APP_ID" : '10864948',#20chu
            "API_KEY" : 'yx9Zc8Rt1LV3eEEq4h6ZGi4M',
            "SECRET_KEY" : 'n9cI3zkVtkBaURsPjg06iFjGt3MNbGp0',},
            {
            "APP_ID" : '10867218',#hong81293
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
            ])
        logging.debug("args:%s"%args)
        client = AipNlp(args["APP_ID"], args["API_KEY"], args["SECRET_KEY"])

    if "client" in locals():
        return client

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def delete_file(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)

def get_voice_from_video(filePath, fm="flv"):
    video = AudioSegment.from_file(filePath, fm)
    return_list = []
    length = len(video)
    for _i in xrange(length/30+1):
        new_file_path = filePath+ "." + str(_i) +".wav"
        video[_i*1000:(_i+30)*1000].export(
            new_file_path,
            format="wav",
            parameters={
                "-acodec":"pcm_s16le",
                "-f":"s16le",
                "-ac":1,
                "-ar":16000})
        return_list.append(new_file_path)
        if _i>20:
            break
    return return_list

def get_voice_from_video_shell(filePath, output_format="pcm"):
    cut_times = 30
    shell_format_string = \
        "ffmpeg -loglevel panic \
-ss %s \
-t %s \
-i %s \
-vn \
-y \
-acodec pcm_s16le \
-f s16le \
-ac 1 \
-ar 16000 \
%s" 
    length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
    re_length = re.compile(length_regexp)

    video_info_output = \
        subprocess.Popen(
            "ffmpeg -i '"+filePath+"' 2>&1 | grep 'Duration'",
            shell = True,
            stdout = subprocess.PIPE
            ).stdout.read()
    logging.debug("video info:\r\n%s"%video_info_output)
    length_match = re_length.search(video_info_output)
    video_length = 0
    if length_match:
        logging.debug("match:%s"%length_match.group(0))
        logging.debug("hour:%s"%length_match.group(1))
        logging.debug("minute:%s"%length_match.group(2))
        logging.debug("second:%s"%length_match.group(3))
        video_length = \
            int(length_match.group(1)) * 3600 +\
            int(length_match.group(2)) * 60 + \
            int(length_match.group(3))
    logging.debug("video length:%s"%(video_length))

    return_list = []
    for _i in xrange(video_length / (cut_times * 1)+1):
        new_file_path = filePath+ "." + str(_i) + "." + output_format
        start_time = time.strftime("%H:%M:%S", time.gmtime(_i*cut_times))
        shell_command = shell_format_string%(
            start_time,
            cut_times,
            filePath,
            new_file_path
        )
        logging.debug("shell command:%s"%shell_command)
        status, output = commands.getstatusoutput(shell_command)
        logging.debug("shell status:%s"%status)
        logging.debug("shell output:%s"%output)
        return_list.append(new_file_path)
    return return_list

def get_sentence_from_voice(client, file_path, file_format="pcm"):
    json_result = client.asr(
        get_file_content(file_path),
        file_format,
        16000,
        {'lan': 'zh',}
    )
    return sep.join(json_result.get("result", []))

def get_words_from_sentence(sentence):
    logging.debug("wait split sentence:%s"%sentence)
    if isinstance(sentence, unicode):
        sentence = sentence.encode("utf8")
    else:
        sentence = sentence

    try_times = 0
    while try_times < baidu_api_error_try_times:
        try_times += 1
        try:
            client = get_baidu_nlp_client("sentence_to_words")
            json_result = client.lexer(sentence)
            logging.debug("baidu return:%s"%(json_result))

            _error_code = json_result.get(u'error_code', False)
            if _error_code:
                logging.error("sentence:%s, result:%s"%(json.dumps(sentence), json.dumps(json_result)))
                continue
            word_list =  reduce(lambda l1,l2:l1+l2, \
                [_word_dict.get("basic_words", []) \
                    if _word_dict.get("ne", "").strip().lower() not in dont_split_ne and \
                        _word_dict.get("pos", "").strip().lower() not in dont_split_pos
                    else [_word_dict.get("item", "")] \
                for _word_dict in json_result.get("items", [])
                ]
            )
            if word_list:
                return word_list
            else:
                continue

        except Exception as e:
            logging.error(str(e), exc_info=True)
            logging.error(repr(sentence))
    return []

def gevent_translate_voice_to_sentence(file_path, save_list, index):
    client = get_baidu_nlp_client("voice_to_sentence")
    json_result = get_sentence_from_voice(client, file_path)
    save_list[index]= json_result
    logging.debug(
            "%s:%s"%(
                file_path,
                json.dumps(json_result, ensure_ascii=False)
                )
            )
    delete_file(file_path)

def get_sentence_from_video(video_file_path):
    _video_file_split_list = get_voice_from_video_shell(video_file_path)

    _sentence_list = [None] * len(_video_file_split_list)

    _multiprocess_list = []
    for _index,_value in enumerate(_video_file_split_list):
        _multiprocess_list.append(pool.spawn(gevent_translate_voice_to_sentence, _value, _sentence_list, _index))
    gevent.joinall(_multiprocess_list)

    return sep.join([_line for _line in _sentence_list if _line])

def save_hashmap(hash_name, key, value):
    red = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    red.hset(hash_name, key, value)

def save_task(redis_task_list_name, data):
    red = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    red.sadd(redis_task_list_name, data if isinstance(data, str) or isinstance(data, unicode) else json.dumps(data))

def count_task(redis_task_list_name):
    red = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    return red.scard(redis_task_list_name)

def get_task(redis_task_list_name):
    red = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    redis_return = red.spop(redis_task_list_name)
    if redis_return and str(redis_return) != "None":
        try:
            logging.debug("task from redis, type:%s, :%s"%(type(redis_return), redis_return))
            return json.loads(redis_return)
        except Exception as e:
            logging.error(str(e), exc_info=True)
            save_hashmap("error", redis_return, traceback.format_exc())
    
def save_result(redis_save_video_result, key, word):
    red = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    red.hset(
        redis_save_video_result,
        key,
        word
    )
    
def api_get_video(data):
    return requests.post(get_video_api, data=data).content

def judge_downloads(data):
    status = json.loads(data).get("is_download")
    if status in [0, 1]:
        return status
    else:
        return -1

def get_video_path(data):
    return json.loads(data).get("video_store_dir")

def loop_task(redis_task_list_name):
    red = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    _wait_run_task_num =  red.scard(redis_task_list_name)
    for _i in xrange(_wait_run_task_num):
        _task = get_task(redis_task_list_name)
        logging.debug("get task from db:%s"%repr(_task))
        _api_response = api_get_video(_task)
        logging.debug("api response:%s"%_api_response)
        download_status = judge_downloads(_api_response)
        logging.debug("api download status:%s"%download_status)
        if download_status > 0:
            _video_uri = get_video_path(_api_response) 
            if _video_uri:
                _sentence = get_sentence_from_video(_video_uri)
                save_result(
                    redis_save_video_result,
                    _task.get("source", "") + "\t" + _task.get("video_id", ""),
                    json.dumps({"subtitle":_sentence, "task":_task})
                )
        else:
            if download_status in (None, -1):
                continue
            if _task and str(_task) != "None":
                save_task(redis_task_list_name, _task)
    return red.scard(redis_task_list_name)

def run_loop_task():
    while 1:
        wait_run_task_num = loop_task(redis_task_list_name)
        logging.info("loop in while:wait run task:%s"%wait_run_task_num)
        time.sleep(1 * 60)

#gevent.spawn(run_loop_task, )
Process(target=run_loop_task, args=()).start()

@app.route("/api/v1/video_to_sentence", methods=["post"])
def get_video():
    try:
        jdata = request.form.to_dict()
        logging.debug("video_to_sentence get post data:%s"%jdata)
        save_status = save_task(redis_task_list_name, jdata)
        # wait_run_task_num = loop_task(redis_task_list_name)
        wait_run_task_num = count_task(redis_task_list_name)
        return json.dumps({"status":save_status, "wait_task":wait_run_task_num})
    except Exception as e:
        logging.error(str(e), exc_info=True)
        return json.dumps({"status":"error, sorry", "detail":traceback.format_exc()})

@app.route("/api/v1/split_sentence_single", methods=["post"])
def get_words_from_sentence_api_single_api():
    return_json = {}
    try:
        # get from request
        jdata = request.form
        logging.debug("get:post data:%s"%jdata)
        sentence = jdata.getlist("sentence")
        if sentence:
            sentence = sentence[0]
        else:
            sentence = ""

        # replace 
        _replace_sentence = re.sub(
                some_emoji_code,
                space_sep,
                re.sub(
                    no_chinese_word_re,
                    space_sep,
                    sentence
                    )
                )
        return_json["words"] = space_sep.join(get_words_from_sentence(_replace_sentence))
        return_json["code"] = 200
    except Exception as e:
        logging.error(str(e), exc_info=True)
        return_json["error"] = "param error"
        return_json["code"] = 404
    return json.dumps(return_json)

@app.route("/api/v1/split_sentence", methods=["post"])
def get_words_from_sentence_api():
    return_json = {}
    try:
        # get from request
        jdata = request.form
        logging.debug("get:post data:%s"%jdata)
        sentence = jdata.getlist("sentence")

        # change type
        if isinstance(sentence, list):
            pass
        elif isinstance(sentence, unicode):
            sentence = [sentence, ]
        elif isinstance(sentence, str):
            sentence = [sentence.decode("utf8")]

        # replace 
        for _index in xrange(len(sentence)):
            _replace_sentence = re.sub(
                some_emoji_code,
                space_sep,
                re.sub(
                    no_chinese_word_re,
                    space_sep,
                    sentence[_index]
                    )
                )
            sentence[_index] = _replace_sentence

        # split to several group
        return_list = [None] * len(sentence)
        _start_index = 0
        _current_index = 0
        _request_max_length = 20000/2
        while _current_index < len(sentence):
            _current_index += 1

            _to_api_sentence_next = sep.join(sentence[_start_index:_current_index+1])
            if len(_to_api_sentence_next) > _request_max_length or \
                    _current_index + 1 > len(sentence):
                _to_api_sentence = sep.join(sentence[_start_index: _current_index])
                _word_list = None
                try_times = baidu_api_error_try_times
                while sentence and try_times > 0:
                    try_times -= 1
                    _word_list = get_words_from_sentence(_to_api_sentence)
                    if _word_list:
                        _word_string = re.sub(sep_replace, sep, space_sep.join(_word_list))
                        _sentence_list = _word_string.split(sep)
                        logging.debug("index from :%s to:%s"%(_start_index, _current_index))
                        
                        if len(_sentence_list) != (_current_index - _start_index):
                            logging.error("\r\n\n\n\n\n%s\n\n\n"%_word_string)
                            continue

                        for _index in xrange(_start_index, _current_index):
                            logging.debug(
                                "return length:%s, index:%s, original length:%s, original index:%s"%(
                                    len(_sentence_list),
                                    _index - _start_index,
                                    len(return_list),
                                    _index),
                                )
                            return_list[_index] = _sentence_list[_index - _start_index]
                        break
                _start_index = copy.deepcopy(_current_index)
            
        return_json["words"] = return_list
        return_json["code"] = 200
    except Exception as e:
        logging.error(str(e), exc_info=True)
        return_json["error"] = "param error"
        return_json["code"] = 404
    return json.dumps(return_json)

def get_listener(host, port):
    from gevent.server import _tcp_listener
    return _tcp_listener((host, port))

def serve_forever(listener, app):
    from gevent import pywsgi
    pywsgi.WSGIServer(listener, app).serve_forever()

def start_server(app, host, port, threads=20):
    listener = get_listener(host, port)
    from multiprocessing import Process
    for _i in range(int(threads)):
        Process(target=serve_forever, args=(listener, app)).start()

if __name__ == "__main__":
    #print get_sentence_from_video(sys.argv[1]) 
    #print json.dumps(get_words_from_sentence(sys.argv[1]), ensure_ascii=False)
    #app.debug = True
    #app.run(host="0.0.0.0", port=7222, processes=1)#, threaded=True)
    #pywsgi.WSGIServer(('0.0.0.0', 7221), app).serve_forever()
    start_server(app, '0.0.0.0', 7221)
    #nohup /opt/virtualenv/asrocr/bin/python asr_baidu_nlp_openapi.py 1>/dev/null 2>&1 &
