import dis


class ServerVerifier(type):

    def __new__(cls, future_class_name, future_class_parents, future_class_attrs):

        lst_argval = []
        for func in future_class_attrs:
            print(func)
            try:
                ret = dis.get_instructions(future_class_attrs[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    lst_argval.append(i.argval)
        if 'connect' in lst_argval:
            raise 'Вызов connect должен отсутствовать для сокетов сервера'
        if 'AF_INET' not in lst_argval or 'SOCK_STREAM' not in lst_argval:
            raise 'Необходимо использовать сокеты для работы по TCP протоколу'

        return type.__new__(cls, future_class_name, future_class_parents, future_class_attrs)
