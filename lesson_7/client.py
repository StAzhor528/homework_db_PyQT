"""Программа-клиент. Разработал Редкин И.А. декабрь 2022 г."""
import dis
import os
import sys
import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
import logging
import threading
import hashlib
import hmac
import binascii

from Crypto.PublicKey import RSA
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

import logs.config_client_log
from client_gui.client_start_gui import UserNameDialog
from client_gui.main_window_gui import ClientMainWindow
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, FROM, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, TO, EXIT, GET_ALL_CLIENTS, ALERT, GET_MY_CONTACTS, PUBLIC_KEY, AUTH, REG, STATE, \
    PASSWORD_HASH, DATA, RESPONSE_511
from common.utils import get_msg, send_msg, log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError

from server_db import ServerStorage

CLIENT_LOGGER = logging.getLogger('client')
socket_lock = threading.Lock()


@log
def arg_parser():
    """Разбор аргументов командной строки при заходе в приложение.
    -a - адрес;
    -p - порт;
    -n - имя клиента;
    -pswd - пароль.
    """
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

    try:
        if '-pswd' in sys.argv:
            password = sys.argv[sys.argv.index('-n') + 1]
        else:
            password = None
    except IndexError:
        CLIENT_LOGGER.error("При запуске клиента после параметра '-pswd' не указано имя.")
        sys.exit(1)

    return address, port, name, password


class ClientVerifier(type):
    """Метакласс. Проверка на корректность класса клиента.
    Вызов accept должен отсутствовать для сокетов клиента.
    Вызов listen должен отсутствовать для сокетов клиента.
    Необходимо использовать сокеты для работы по TCP протоколу.
    Сокеты на уровне классов создавать запрещено
    """

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


class Client(threading.Thread, QObject):
    """Основной класс. Обменивается информацией с сервером."""
    my_contacts = []
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username, password, keys, state):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.db = database
        self.port = port
        self.address = ip_address
        self.name = username
        self.password = password
        self.keys = keys
        self.state = state
        self.passwd_hash = ''
        self.running = True
        self.connection_init()

    def connection_init(self):
        """Установка соединение с сервером. Выявление ошибок при подключении и передачи приветственного сообщения."""
        print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {self.name}')
        CLIENT_LOGGER.info(
            f'Запущен клиент с параметрами: адрес сервера: {self.address}, '
            f'порт: {self.port}, имя пользователя: {self.name}')

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.address, self.port))
            send_msg(self.sock, self.create_presence(self.name, self.password, self.state))
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

    @log
    def create_exit_message(self, account_name):
        """Создает сообщение EXIT."""
        return {
            ACTION: EXIT,
            TIME: str(datetime.now()),
            ACCOUNT_NAME: account_name
        }

    @log
    def message_from_server(self, sock, my_username):
        """Принимает сообщение с сервера или список всех клиентов сервера."""
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
                    self.new_message.emit(self.message[FROM])

                elif self.message[RESPONSE] == 202:
                    print(f'Получен следующий список всех клиентов сервера: {self.message[ALERT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {self.message}')
            except IncorrectDataRecivedError:
                CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                self.connection_lost.emit()
                break

    @log
    def create_message(self, sock, account_name='Guest'):
        """Создает сообщение для другого пользователя."""
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

    def send_message(self, from_user, to_user, message):
        """Создает словорб сообщения и отправляет его на сервер."""
        self.message_dict = {
            ACTION: MESSAGE,
            FROM: from_user,
            TO: to_user,
            TIME: str(datetime.now()),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {self.message_dict}')
        try:
            send_msg(self.sock, self.message_dict)
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception as e:
            print(e)
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @log
    def add_contact(self, account_name):
        """Добавляет контакта в список контактов."""
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
        """Удаляет клиента из списка контактов."""
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
        """Выдает список всех сообщений из базы данных."""
        return self.db.get_all_users_messages(account_name)

    @log
    def get_all_clients(self, sock, account_name):
        """Отправляет запрос на сервер для получения списка всех контактов."""
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
        """Интерактивное управление запросами в терминале."""
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
    def create_presence(self, account_name, password, state):
        """Создает приветственное сообщение."""
        passwd_bytes = password.encode('utf-8')
        salt = account_name.lower().encode('utf-8')
        self.passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        self.passwd_hash_str = binascii.hexlify(self.passwd_hash).decode('ascii')

        pubkey = self.keys.publickey().export_key().decode('ascii')
        out = {
            ACTION: PRESENCE,
            TIME: str(datetime.now()),
            USER: {
                ACCOUNT_NAME: account_name,
                PUBLIC_KEY: pubkey,
                PASSWORD_HASH: self.passwd_hash_str,
                STATE: state
            }
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    def print_help(self):
        """Инструкция использования интерактивного управления через терминал."""
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
        """Разбирает приветственное сообщение от сервера."""
        CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {msg}')
        if RESPONSE in msg:
            if msg[RESPONSE] == 200:
                return '200 : OK'
            elif msg[RESPONSE] == 400:
                raise ServerError(f'400 : {msg[ERROR]}')
            elif msg[RESPONSE] == 511 :
                msg_data = msg[DATA]
                hash = hmac.new(self.passwd_hash_str.encode('ascii'), msg_data.encode('ascii'), 'MD5')
                digest = hash.digest()
                msg_to_server = RESPONSE_511
                msg_to_server[DATA] = binascii.b2a_base64(digest).decode('ascii')
                send_msg(self.sock, msg_to_server)
                return
        raise ReqFieldMissingError(RESPONSE)

    def run(self):
        '''Метод содержащий основной цикл работы транспортного потока.'''
        CLIENT_LOGGER.debug('Запущен процесс - приёмник собщений с сервера.')
        self.receiver = threading.Thread(target=self.message_from_server, args=(self.sock, self.name))
        self.receiver.daemon = True
        self.receiver.start()

        # self.user_interface = threading.Thread(target=self.user_interactive, args=(self.sock, self.name))
        # self.user_interface.daemon = True
        # self.user_interface.start()
        # CLIENT_LOGGER.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if self.receiver.is_alive():
                continue
            break


if __name__ == '__main__':
    server_address, server_port, client_name, client_passwd = arg_parser()
    state = AUTH
    client_app = QApplication(sys.argv)
    client_app.setStyle('Fusion')

    if not client_name or not client_passwd:
        start_dialog = UserNameDialog()
        start_dialog.show()
        client_app.exec_()
        if start_dialog.name_pass:
            client_name = start_dialog.name_pass[0]
            client_passwd = start_dialog.name_pass[1]
            state = AUTH
            CLIENT_LOGGER.info(f'Клиент USERNAME = {client_name}, PASSWD = {client_passwd} пытается авторизоваться.')
        elif start_dialog.name_pass_reg:
            client_name = start_dialog.name_pass_reg[0]
            client_passwd = start_dialog.name_pass_reg[1]
            state = REG
            CLIENT_LOGGER.info(f'Регистрация USERNAME = {client_name}, PASSWD = {client_passwd}.')
        else:
            exit(0)

    # Загружаем ключи с файла, если же файла нет, то генерируем новую пару.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())


    database = ServerStorage()
    try:
        transport = Client(
            server_port,
            server_address,
            database,
            client_name,
            client_passwd,
            keys,
            state)
    except ServerError as e:
        print(e.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()
    time.sleep(1)
    if state == AUTH:
        main_window = ClientMainWindow(database, transport)
        main_window.make_connection(transport)
        main_window.setWindowTitle(f'Чат {client_name}')
        client_app.exec_()


