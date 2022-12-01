import logging
import os

log = logging.getLogger('client')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'app.main.log')
formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(module)s - %(message)s")

fh = logging.FileHandler(PATH, encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

log.addHandler(fh)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    cons = logging.StreamHandler()
    cons.setLevel(logging.DEBUG)
    cons.setFormatter(formatter)
    log.addHandler(cons)
    log.info('Тестовый запуск')
