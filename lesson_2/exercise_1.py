import dis
from socket import socket


class ClientVerifier(type):

    def __new__(cls, future_class_name, future_class_parents, future_class_attrs):
        lst_argval = []
        for func in future_class_attrs:
            try:
                ret = dis.get_instructions(future_class_attrs[func])
            except TypeError:
                pass

            else:
                for i in ret:
                    lst_argval.append(i.argval)
        if 'accept' in lst_argval:
            raise 'Вызов accept должен отсутствовать для сокетов клиента'
        elif 'listen' in lst_argval:
            raise 'Вызов listen должен отсутствовать для сокетов клиента'
        if 'AF_INET' not in lst_argval or 'SOCK_STREAM' not in lst_argval:
            raise 'Необходимо использовать сокеты для работы по TCP протоколу'
        for val in future_class_attrs.values():
            if type(val) == socket:
                raise 'Сокеты на уровне классов создавать запрещено'

        return type.__new__(cls, future_class_name, future_class_parents, future_class_attrs)
