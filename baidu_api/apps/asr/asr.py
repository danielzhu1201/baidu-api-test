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
import base64
import hashlib
import random
import logging
import requests
import commands
import traceback
import subprocess
import multiprocessing
from multiprocessing import Process
from SSDB import SSDB

sys.path.append("./")
from apps import app

from apps.client.client import get_baidu_nlp_client

import gevent
import gevent.pool
import gevent.monkey
gevent.monkey.patch_socket()
pool=gevent.pool.Pool(40)

from config.config import ssdb_host 
from config.config import ssdb_port 
from config.config import ssdb_save_participle_result_hashmap 
from config.config import redis_host 
from config.config import redis_port 
from config.config import redis_db 
from config.config import redis_task_list_name 
from config.config import redis_save_video_result 
from config.config import get_video_api 
from config.config import baidu_api_error_try_times 
from config.config import space_sep 
from config.config import sep 
from config.config import sep_replace 
from config.config import no_chinese_word_re 
from config.config import some_emoji_code 
from config.config import dont_split_pos 
from config.config import dont_split_ne 
from config.config import VIDEO_TO_SENTENCE_THREADS


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def delete_file(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)

class ssdb_connect():
    def __init__(self):
        self.ssdb = SSDB(host=ssdb_host, port=ssdb_port)
    def ssdb_save_hashmap(self, ssdb_save_participle_result_hashmap, key, value):
        status = self.ssdb.request("hset",[ssdb_save_participle_result_hashmap, key, value])
        logging.debug("ssdb,hset,hashmap:%s,key:%s,status:%s"%(ssdb_save_participle_result_hashmap, key, status))
        return status

    def ssdb_get_hashmap(self, ssdb_save_participle_result_hashmap, key):
        result = self.ssdb.request("hget", [ssdb_save_participle_result_hashmap, key])
        logging.debug("ssdb,hget,hashmap:%s,key:%s,value:%s"%(ssdb_save_participle_result_hashmap, key, result))
        return result

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
    logging.info("video length:%s"%(video_length))

    return_list = []
    if video_length:
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
    sentence_base64 = hashlib.md5(base64.b64encode(sentence)).hexdigest()

    baidu_response = None
    ssdb = ssdb_connect()
    exists_data = ssdb.ssdb_get_hashmap(ssdb_save_participle_result_hashmap, sentence_base64)
    if exists_data and exists_data.data:
        logging.debug("%s, participle exists, base64:%s"%(sentence, sentence_base64))
        baidu_response = json.loads(exists_data.data)
    else:
        logging.debug("%s, participle does not exists, base64:%s"%(sentence, sentence_base64))

    try_times = 0
    while 1:
        if baidu_response:
            word_list =  reduce(lambda l1,l2:l1+l2, \
                    [_word_dict.get("basic_words", []) \
                        if _word_dict.get("ne", "").strip().lower() not in dont_split_ne and \
                            _word_dict.get("pos", "").strip().lower() not in dont_split_pos
                        else [_word_dict.get("item", "")] \
                    for _word_dict in baidu_response.get("items", [])
                    ]
                )
            if word_list:
                return word_list

        if try_times < (baidu_api_error_try_times + 1):
            pass
        else:
            break

        try_times += 1
        try:
            client = get_baidu_nlp_client("sentence_to_words")
            json_result = client.lexer(sentence)
            logging.debug("baidu return:%s"%(json.dumps(json_result, indent=4, ensure_ascii=False)))

            _error_code = json_result.get(u'error_code', False)
            if _error_code:
                logging.error("sentence:%s, result:%s"%(json.dumps(sentence), json.dumps(json_result)))
                continue
            else:
                baidu_response = json_result
                ssdb.ssdb_save_hashmap(ssdb_save_participle_result_hashmap, sentence_base64, json.dumps(json_result))
        except Exception as e:
            logging.error(str(e), exc_info=True)
            logging.error(repr(sentence))


    return []

def gevent_translate_voice_to_sentence(file_path, save_list, index):
    client = get_baidu_nlp_client("voice_to_sentence")
    json_result = get_sentence_from_voice(client, file_path)
    save_list[index]= json_result
    logging.info(
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
    logging.debug("request :%s get download status, data:%s"%(get_video_api, data))
    try:
        with gevent.Timeout(3, False) as timeout:
            api_response =  requests.post(get_video_api, data=data).content
            return api_response
    except:
        return "{}"

def judge_downloads(data):
    try:
        status = json.loads(data).get("is_download")
        if status in [0, 1, 2]:
            return status
    except Exception as e:
        logging.error(str(e), exc_info=True)

    return -1

def get_video_path(data):
    return json.loads(data).get("video_store_dir")

def loop_task(redis_task_list_name):
    _wait_run_task_num =  count_task(redis_task_list_name)
    logging.info("exists task:%s"%_wait_run_task_num)
    pool = multiprocessing.Pool(VIDEO_TO_SENTENCE_THREADS)
    logging.info("create multiprocessing pool:%s"%VIDEO_TO_SENTENCE_THREADS)
    _all_task = [get_task(redis_task_list_name) for _ in xrange(_wait_run_task_num)]
    logging.info("collect task done, wait to input pool")
    pool.map(single_video_translate_task, _all_task)
    logging.info("add task to pool done :%s"%_wait_run_task_num)
    pool.close()
    pool.join()
    logging.info("add  task done:%s"%datetime.datetime.now())
    return _wait_run_task_num

def single_video_translate_task(_task):
    if _task:
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
                    json.dumps({"subtitle":_sentence, "subtitle_status":download_status, "task":_task})
                )
        elif download_status == -1:
            logging.error("task:%s,response:%s"%(_task, _api_response))
        elif download_status == 0:
            logging.info("task:%s, response:%s"%(_task, _api_response))
            if _task and str(_task) != "None":
                save_task(redis_task_list_name, _task)

def run_loop_task():
    while 1:
        try:
            wait_run_task_num = loop_task(redis_task_list_name)
            logging.info("loop in while:wait task:%s"%wait_run_task_num)
        except Exception as e:
            logging.error(str(e), exc_info=True)
        time.sleep(1 * 10)

def get_video(request):
    try:
        jdata = request.form.to_dict()
        logging.debug("api:video_to_sentence:get post data:%s"%jdata)
        save_status = save_task(redis_task_list_name, jdata)
        wait_run_task_num = count_task(redis_task_list_name)
        return json.dumps({"status":save_status, "wait_task":wait_run_task_num})
    except Exception as e:
        logging.error(str(e), exc_info=True)
        return json.dumps({"status":"error, sorry", "detail":traceback.format_exc()})

def get_words_from_sentence_api_single_api(request):
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

def get_words_from_sentence_api(request):
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

if __name__ == "__main__":
    #print get_sentence_from_video(sys.argv[1]) 
    #print json.dumps(get_words_from_sentence(sys.argv[1]), ensure_ascii=False)
    #app.debug = True
    #app.run(host="0.0.0.0", port=7222, processes=1)#, threaded=True)
    #pywsgi.WSGIServer(('0.0.0.0', 7221), app).serve_forever()
    Process(target=run_loop_task, args=()).start()
    #start_server(app, '0.0.0.0', SERVER_PORT, threads=THREADS_NUM)
    #nohup /opt/virtualenv/asrocr/bin/python asr_baidu_nlp_openapi.py 1>/dev/null 2>&1 &
