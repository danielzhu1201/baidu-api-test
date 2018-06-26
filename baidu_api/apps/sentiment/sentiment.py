import sys
sys.path.append("./")

import json

from apps.client.client import get_baidu_nlp_client

import logging
logger = logging.getLogger("sentiment")

mark = "0:negative, 1:, 2:positive"

def parse_api(response):
    try:
        return response["items"][0]["sentiment"]
    except Exception as e:
        logger.error(str(e), exc_info=True)
        return None

def sentiment(request, ):
    sentiment_code = None
    http_code = 500

    jdata = request.form
    logger.debug("get:post data:%s"%jdata)
    sentence = jdata.getlist("text")

    if sentence:
        sentence = sentence[0]
    else:
        sentence = ""

    if isinstance(sentence, unicode):
        sentence = sentence.encode("utf8")
    else:
        sentence = sentence

    client = get_baidu_nlp_client()
    try:
        result = client.sentimentClassify(sentence)    
        sentiment_code = parse_api(result)
        http_code = 200
    except Exception as e:
        logger.error(str(e), exc_info=True)
    return json.dumps({"code":http_code, "sentiment":sentiment_code, "mark":mark})
