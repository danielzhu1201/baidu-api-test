#coding:utf8
import sys
sys.path.append("./")
import pandas as pd
import time
import re
from client import get_baidu_nlp_client
from client import accounts
from multiprocessing import Pool
#import win_unicode_console

#win_unicode_console.enable()
pat_re = '([^\u4E00-\u9FA5a-zA-Z0-9]+)'
client = get_baidu_nlp_client(0)

def func(sentence):
    try:
        json_result = client.lexer(sentence)
    except:
        #import sys
        #sys.exit()
        pass
    else:
        if json_result.get(u'error_msg',''):
            print ','
    time.sleep(0.1)


if __name__ == '__main__':
    data = pd.read_csv("video_title.csv")
    sentences = []
    for i in range(0, len(data)):
        #sentences.insert(i+1, re.sub(pat_re, '', data['video_title'][i]))
        sentences.insert(i+1, data['video_title'][i])
    
    for i in range(2,3):
        print i
        print accounts[i]
        client = get_baidu_nlp_client(i)
        pool = Pool(2)
        t1 = time.time()
        pool.map(func, sentences)
        pool.close()
        pool.join()
        t2 = time.time()
        print '\n\n\n\nclient id = ' + accounts[i]["APP_ID"]
        print (t2-t1)
        print '\n\n\n\n'

# cd desktop\baidu_test  python multi_process.py

#pool.map会对每一个线程存有一个status，最后join的时候会监测才能join的 -- 所以如果中间sys.exit就会导致有一个永远无法结束
