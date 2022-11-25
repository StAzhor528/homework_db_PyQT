"""Программа-клиент"""
import dis
import sys
import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
import logging
import threading
import logs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, FROM, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, TO, EXIT, GET_ALL_CLIENTS, ALERT, GET_MY_CONTACTS
from common.utils import get_msg, send_msg, log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError

# from server_db import ServerStorage
from lesson_8.server_db import ServerStorage

CLIENT_LOGGER = logging.getLogger('client')


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


class Client(metaclass=ClientVerifier):
    my_contacts = []

    def __init__(self, database):
        self.db = database

    @log
    def create_exit_message(self, account_name):
        return {
            ACTION: EXIT,
            TIME: str(datetime.now()),
            ACCOUNT_NAME: account_name
        }

    @log
    def message_from_server(self, sock, my_username):
        while True:
            try:
                self.message = get_msg(sock)
                if ACTION in self.message and self.message[ACTION] == MESSAGE and \
                        FROM in self.message and TO in self.message \
                        and MESSAGE_TEXT in self.message and self.message[TO] == my_username:
                    print(f'\nПолучено сообщение от пользователя {self.message[FROM]}:'
                          f'\n{self.message[MESSAGE_TEXT]}')
                    CLIENT_LOGGER.info(f'Получено сообщение от пользователя {self.message[FROM]}:'
                                       f'\n{self.message[MESSAGE_TEXT]}')
                elif self.message[RESPONSE] == 202:
                    print(f'Получен следующий список всех клиентов сервера: {self.message[ALERT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {self.message}')
            except IncorrectDataRecivedError:
                CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break

    @log
    def create_message(self, sock, account_name='Guest'):
        self.to_user = input('Введите получателя сообщения: ')
        self.message = input('Введите сообщение для отправки: ')
        self.message_dict = {
            ACTION: MESSAGE,
            FROM: account_name,
            TO: self.to_user,
            TIME: str(datetime.now()),
            MESSAGE_TEXT: self.message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {self.message_dict}')
        try:
            send_msg(sock, self.message_dict)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {self.to_user}')
        except Exception as e:
            print(e)
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @log
    def add_contact(self, account_name):
        self.contact_name = input('Введите логин пользователя для добавления его в список контактов: ')
        self.my_contacts = self.db.get_my_contacts(account_name)
        if self.contact_name == account_name:
            print(f'Вы ввели свой ник')
            return
        elif self.contact_name in self.my_contacts:
            print(f'Пользователь {self.contact_name} уже в вашем списке')
            return

        self.my_contacts.append(self.contact_name)
        self.db.insert_in_contactdb(account_name, self.contact_name, '', str(datetime.now()))
        print(f'Пользователь {self.contact_name} добавлен в ваш список контактов')

    @log
    def del_contact(self, account_name):
        self.contact_name = input('Введите логи пользователя для удаления его из списка контактов: ')
        self.my_contacts = self.db.get_my_contacts(account_name)
        if self.contact_name == account_name:
            print(f'Вы ввели свой логин')
            return
        elif self.contact_name not in self.my_contacts:
            print(f'Пользователя {self.contact_name} нет в вашем списке')
            return

        self.my_contacts.remove(self.contact_name)
        self.db.del_in_contactdb(account_name, self.contact_name)
        print(f'Пользователь {self.contact_name} удален из вашего списка контактов')

    @log
    def get_message_history(self, account_name):
        self.db.get_all_users_messages(account_name)

    @log
    def get_all_clients(self, sock, account_name):
        self.get_contacts_dict = {
            ACTION: GET_ALL_CLIENTS,
            TIME: str(datetime.now()),
            ACCOUNT_NAME: account_name
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь для получения списка всех контактов: {self.get_contacts_dict}')
        try:
            send_msg(sock, self.get_contacts_dict)
            CLIENT_LOGGER.info(f'Отправлен запрос на сервер для получения списка контактов')
        except Exception as e:
            print(e)
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)


    @log
    def user_interactive(self, sock, username):
        self.print_help()
        while True:
            self.command = input('Введите команду: ')
            if self.command == 'message':
                self.create_message(sock, username)
            elif self.command == 'help':
                self.print_help()
            elif self.command == 'get_all_clients':
                self.get_all_clients(sock, username)
                time.sleep(0.5)
            elif self.command == 'get_my_contacts':
                self.my_contacts = self.db.get_my_contacts(username)
                print(self.my_contacts)
                time.sleep(0.5)
            elif self.command == 'add_contact':
                self.add_contact(username)
                time.sleep(0.5)
            elif self.command == 'del_contact':
                self.del_contact(username)
                time.sleep(0.5)
            elif self.command == 'message_history':
                self.get_message_history(username)
                time.sleep(0.5)
            elif self.command == 'exit':
                send_msg(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')

                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @log
    def create_presence(self, account_name):
        out = {
            ACTION: PRESENCE,
            TIME: str(datetime.now()),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('get_all_clients - получение списка всех подключенных клиентов')
        print('get_my_contacts - получение списка моих контактов')
        print('add_contact - добавление клиента в список моих контактов')
        print('del_contact - удаление клиента из списка моих контактов')
        print('message_history - история сообщений')
        print('exit - выход из программы')

    @log
    def process_response_ans(self, msg):
        CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {msg}')
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200 : OK'
            elif msg[RESPONSE] == 400:
                raise ServerError(f'400 : {msg[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @log
    def arg_parser(self):
        try:
            if '-p' in sys.argv:
                port = int(sys.argv[sys.argv.index('-p') + 1])
            else:
                port = DEFAULT_PORT
            if port < 1024 or port > 65535:
                raise ValueError
        except IndexError:
            CLIENT_LOGGER.error("При запуске клиента после параметра '-p' не указан номер порта.")
            sys.exit()
        except ValueError:
            CLIENT_LOGGER.error('При запуске клиента неверно указан номер порта.')
            sys.exit(1)

        try:
            if '-a' in sys.argv:
                address = sys.argv[sys.argv.index('-a') + 1]
            else:
                address = DEFAULT_IP_ADDRESS
        except IndexError:
            CLIENT_LOGGER.error("При запуске клиента после параметра '-a' не указан адрес.")
            sys.exit(1)

        try:
            if '-n' in sys.argv:
                name = sys.argv[sys.argv.index('-n') + 1]
            else:
                name = None
        except IndexError:
            CLIENT_LOGGER.error("При запуске клиента после параметра '-n' не указано имя.")
            sys.exit(1)

        return port, address, name

    def main(self):
        self.port, self.address, self.name = self.arg_parser()

        print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {self.name}')

        if not self.name:
            self.name = input('Введите имя пользователя: ')

        CLIENT_LOGGER.info(
            f'Запущен клиент с параметрами: адрес сервера: {self.address}, '
            f'порт: {self.port}, имя пользователя: {self.name}')

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.address, self.port))
            send_msg(self.sock, self.create_presence(self.name))
            self.answer = self.process_response_ans(get_msg(self.sock))
            CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {self.answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            CLIENT_LOGGER.critical(
                f'Не удалось подключиться к серверу {self.address}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            self.receiver = threading.Thread(target=self.message_from_server, args=(self.sock, self.name))
            self.receiver.daemon = True
            self.receiver.start()

            self.user_interface = threading.Thread(target=self.user_interactive, args=(self.sock, self.name))
            self.user_interface.daemon = True
            self.user_interface.start()
            CLIENT_LOGGER.debug('Запущены процессы')

            while True:
                time.sleep(1)
                if self.receiver.is_alive() and self.user_interface.is_alive():
                    continue
                break


if __name__ == '__main__':
    database = ServerStorage()
    client = Client(database)
    client.main()
