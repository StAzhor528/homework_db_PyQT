"""Запуск несколькоих клиентов из терминала."""
import subprocess
import os
import time

if __name__ == '__main__':
    PROCESSES = []

    while True:
        ACTION = input('Выберите действие: q - выход, '
                       's - запустить сервер и клиенты, '
                       'x - закрыть все окна: ')

        if ACTION == 'q':
            break
        elif ACTION == 's':
            PROCESSES.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
            time.sleep(0.5)
            PROCESSES.append(subprocess.Popen('python client.py -n test1',
                                              creationflags=subprocess.CREATE_NEW_CONSOLE))
            time.sleep(0.5)
            PROCESSES.append(subprocess.Popen('python client.py -n test2',
                                              creationflags=subprocess.CREATE_NEW_CONSOLE))
            time.sleep(0.5)
            PROCESSES.append(subprocess.Popen('python client.py -n test3',
                                              creationflags=subprocess.CREATE_NEW_CONSOLE))
            time.sleep(0.5)
        elif ACTION == 'x':
            while PROCESSES:
                VICTIM = PROCESSES.pop()
                VICTIM.kill()
