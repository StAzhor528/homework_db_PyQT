import platform
from subprocess import PIPE, call
from threading import Thread


def address_ping(ip_address, ip_dict):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    result = call(command, stdout=PIPE)
    if result == 0:
        ip_dict['Доступные узлы'].append(ip_address)
    else:
        ip_dict['Недоступные узлы'].append(ip_address)


def host_ping(ip_addresses):
    ip_dict = {
        'Доступные узлы': [],
        'Недоступные узлы': [],
    }
    threads = []
    for ip_address in ip_addresses:
        t = Thread(target=address_ping, args=(ip_address, ip_dict))
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return ip_dict


if __name__ == '__main__':
    ip_addresses = []
    for i in list(range(100)):
        ip_addresses.append('192.168.1.1')

    result = host_ping(ip_addresses)
    print(result)
