import os
import sys
import yaml

import logging
import traceback

if not os.path.isfile("config.yaml"):
    sys.exit("'config.yaml' not found! Please add it and try again.")
else:
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

logfile = config["log"]
log = logging.getLogger("my_log")
log.setLevel(logging.INFO)
FH = logging.FileHandler(logfile, encoding='utf-8')
str_logging_format = "%(asctime)s-%(levelname)s-%(message)s"
log_format = '%(asctime)s : [%(levelname)s] : %(message)s'
basic_formater = logging.Formatter(log_format)
FH.setFormatter(basic_formater)
log.addHandler(FH)


def log_init():
    return log


## функция для записи в лог сообщений об ошибке
def error_log(line_no):
    ## задаем формат ошибочных сообщений, добавляем номер строки
    err_formater = logging.Formatter('%(asctime)s : [%(levelname)s][LINE ' + line_no + '] : %(message)s')
    ## устанавливаем формат ошибок в логгер
    FH.setFormatter(err_formater)
    log.addHandler(FH)
    ## пишем сообщение error
    log.error(traceback.format_exc())
    ## возвращаем базовый формат сообщений
    FH.setFormatter(basic_formater)
    log.addHandler(FH)
