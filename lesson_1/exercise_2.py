import ipaddress
import re

import ecxercise_1


def host_range_ping():
    while True:
        ip_address = input("Введите ip адресс: ")
        ip_lst = []
        if re.match('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', ip_address):
            while True:
                number_of_ip_addresses = int(
                    input('Введите количество ip адресов для проверки после исходного адреса: '))
                limit = int(ip_address.split('.')[-1]) + number_of_ip_addresses
                if limit > 255:
                    print('Меняться может только последний октет исходного адреса!')
                    continue
                else:
                    ip_obj = ipaddress.ip_address(ip_address)
                    for i in list(range(number_of_ip_addresses)):
                        ip_lst.append(str(ip_obj + i))
                    break
            return ecxercise_1.host_ping(ip_lst)

        else:
            print('IP адрес введен не корректно!\n'
                  'Повторите попытку')
            continue


if __name__ == '__main__':
    result = host_range_ping()
    print(result)
