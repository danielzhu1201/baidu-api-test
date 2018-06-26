from flask import Flask
from flask import request
app = Flask(__name__)

import logging
logging_level = logging.DEBUG
logging_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
logging.basicConfig(level=logging_level, format=logging_format)
logging.getLogger().setLevel(logging_level)
logging.getLogger('werkzeug').setLevel(logging_level)
logging.getLogger("requests").setLevel(logging_level)
logging.getLogger('urllib3').setLevel(logging_level)

import os
log_path = "./log"
if os.path.exists(log_path):
    pass
else:
    os.mkdir(log_path)

import logging
import logging.config
logging.config.fileConfig("config/log_config.config")
