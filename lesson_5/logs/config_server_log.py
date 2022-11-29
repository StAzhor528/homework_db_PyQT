import logging
import os
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger('server')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'app.main.log')

formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(module)s - %(message)s")


trf_handler = TimedRotatingFileHandler(PATH, when='midnight', encoding='utf-8')
trf_handler.setLevel(logging.DEBUG)
trf_handler.setFormatter(formatter)

log.addHandler(trf_handler)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    log.addHandler(console)
    log.info('Тестовый запуск')
