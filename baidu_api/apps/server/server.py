#coding:utf8
from config.config import SERVER_PORT
from config.config import THREADS_NUM
from apps.asr.asr import get_words_from_sentence_api
from apps.asr.asr import get_words_from_sentence_api_single_api
from apps.asr.asr import get_video
from apps.sentiment.sentiment import sentiment

import sys
sys.path.append("./")

from apps import app
from apps import request

@app.route("/api/v1/split_sentence", methods=["post"])
def get_words_from_sentence_api_flask():
    return get_words_from_sentence_api(request)

@app.route("/api/v1/split_sentence_single", methods=["post"])
def get_words_from_sentence_api_single_api_flask():
    return get_words_from_sentence_api_single_api(request)

@app.route("/api/v1/video_to_sentence", methods=["post"])
def get_video_flask():
    return get_video(request)

@app.route("/api/v1/sentiment", methods=["post"])
def sentiment_flask():
    return sentiment(request)

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

def start():
    #Process(target=run_loop_task, args=()).start()
    start_server(app, '0.0.0.0', SERVER_PORT, threads=THREADS_NUM)

