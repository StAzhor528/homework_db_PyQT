import subprocess

PROCESSES = []
PROCESSES.append(subprocess.Popen('python server.py',
                                  creationflags=subprocess.CREATE_NEW_CONSOLE))
