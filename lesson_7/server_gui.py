"""Графический интерфейс для работы с сервером."""

import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import os


def create_users_table(database):
    list_users = [(user.id, user.login, user.info) for user in database.get_all_users()]
    users_table = QStandardItemModel()
    users_table.setVerticalHeaderLabels(['ID', 'Login', 'INFO'])
    for user in list_users:
        user_id, user_login, user_info = user
        user_id = QStandardItem(user_id)
        user_id.setEditable(False)
        user_login = QStandardItem(user_login)
        user_login.setEditable(False)
        user_info = QStandardItem(user_info)
        user_info.setEditable(False)
        users_table.appendRow([user_id, user_login, user_info])
    return users_table


def create_messages_table(database):
    msg_lst = database.get_all_messages()

    msg_table = QStandardItemModel()
    msg_table.setHorizontalHeaderLabels(['От кого', 'Кому', 'Сообщение', 'Время'])
    for msg in msg_lst:
        from_client, to_client, msg_text, time = msg
        from_client = QStandardItem(from_client)
        from_client.setEditable(False)
        to_client = QStandardItem(to_client)
        to_client.setEditable(False)
        msg_text = QStandardItem(msg_text)
        msg_text.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        msg_table.appendRow([from_client, to_client, msg_text, time])
    return msg_table


class MainWindow(QMainWindow):
    """Основное окно"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Кнопка выхода на тулбаре
        self.exit_action = QAction('Выход', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(qApp.quit)

        # Кнопка обновления списка клиентов на тулбаре
        self.refresh_action = QAction('Обновить список', self)

        # Кнопка для вывода истории сообщений на тулбаре
        self.msg_history_action = QAction('История сообщений', self)

        # Кнопка для настройки сервера на тулбаре
        self.config_action = QAction('Настройка сервера', self)

        # Статусбар
        self.statusBar()

        # Тулбар
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exit_action)
        self.toolbar.addAction(self.refresh_action)
        self.toolbar.addAction(self.msg_history_action)
        self.toolbar.addAction(self.config_action)

        # Размеры основного окна
        self.setFixedSize(450, 400)
        self.setWindowTitle('Server Ivan Redkin')

        # Наименование таблицы
        self.table_title = QLabel('Списко всех клиентов', self)
        self.table_title.setFixedSize(400, 15)
        self.table_title.move(10, 35)

        # Таблица всех клиентов
        self.clients_table = QTableView(self)
        self.clients_table.setFixedSize(430, 300)
        self.clients_table.move(10, 55)

        # Отобразить окно
        self.show()



class HistoryMsgWindow(QDialog):
    """Окно с историей сообщений."""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна
        self.setWindowTitle('История сообщений')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнопка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # Таблица истории сообщений
        self.msg_history_table = QTableView(self)
        self.msg_history_table.move(10, 10)
        self.msg_history_table.setFixedSize(580, 620)

        # Отобразить окно
        self.show()



class ConfigWindow(QDialog):
    """Окно настроек."""

    def __init__(self):
        super(ConfigWindow, self).__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна
        self.setFixedSize(375, 240)
        self.setWindowTitle('Настройки')

        # Надпись 'Путь до файла БД'
        self.db_path_label = QLabel('Путь до файла БД: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # Отображение пути до файла БД
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 25)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути
        self.db_path_button = QPushButton('Путь...', self)
        self.db_path_button.move(275, 28)

        # Функция обработчик кнопки выбора пути к файлу БД
        def open_file_bd():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_button.clicked.connect(open_file_bd)

        # Надпись 'Имя файла БД'
        self.db_name_label = QLabel('Имя файла БД: ', self)
        self.db_name_label.move(10, 68)
        self.db_name_label.setFixedSize(180, 27)

        # Отображение пути до файла БД
        self.db_name = QLineEdit(self)
        self.db_name.setFixedSize(257, 27)
        self.db_name.move(110, 68)

        # Надпись 'Порт'
        self.db_port_label = QLabel('Порт: ', self)
        self.db_port_label.move(10, 108)
        self.db_port_label.setFixedSize(180, 27)

        # Ввод номера порта
        self.db_name = QLineEdit(self)
        self.db_name.setFixedSize(257, 27)
        self.db_name.move(110, 108)

        # Надпись 'IP'
        self.db_ip_label = QLabel('IP: ', self)
        self.db_ip_label.move(10, 148)
        self.db_ip_label.setFixedSize(180, 27)

        # Ввод IP
        self.db_ip = QLineEdit(self)
        self.db_ip.setFixedSize(257, 27)
        self.db_ip.move(110, 148)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(10, 200)

        # # Кнопка сохранения настроек
        self.close_btn = QPushButton('Закрыть', self)
        self.close_btn.move(275, 200)
        self.close_btn.clicked.connect(self.close)

        self.show()


# if __name__ == '__main__':
    # -------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------
    # 1. Проверка работы основново окна.
    # app = QApplication(sys.argv)
    # main_window = MainWindow()
    # main_window.statusBar().showMessage('Текст для статусбара')
    # test_list = QStandardItemModel(main_window)
    # test_list.setHorizontalHeaderLabels(['ID', 'Login', 'INFO'])
    # test_list.appendRow([QStandardItem('1'), QStandardItem('test1'), QStandardItem('test1')])
    # test_list.appendRow([QStandardItem('2'), QStandardItem('test2'), QStandardItem('test2')])
    # test_list.appendRow([QStandardItem('3'), QStandardItem('test3'), QStandardItem('test3')])
    # main_window.clients_table.setModel(test_list)
    # main_window.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    # main_window.clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    # app.exec_()
    #
    # -------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------
    #
    # 2. Проверка работы окна историй сообщений.
    # app = QApplication(sys.argv)
    # history_window = HistoryMsgWindow()
    # test_list = QStandardItemModel(history_window)
    # test_list.setHorizontalHeaderLabels(['От кого', 'Кому', 'Сообщение', 'Время'])
    # test_list.appendRow(
    #     [QStandardItem('test1'), QStandardItem('test2'), QStandardItem('Привет'), QStandardItem('01.01.01 00:00:00')])
    # test_list.appendRow(
    #     [QStandardItem('test2'), QStandardItem('test3'), QStandardItem('Привет тебе'), QStandardItem('02.02.02 01:01:01')])
    # test_list.appendRow(
    #     [QStandardItem('test3'), QStandardItem('test1'), QStandardItem('Пока'), QStandardItem('03.03.03 02:02:02')])
    # history_window.msg_history_table.setModel(test_list)
    # history_window.msg_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    # history_window.msg_history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    # app.exec_()
    #
    # -------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------
    #
    # 3. Проверка работы окна настроек.
    # app = QApplication(sys.argv)
    # dial = ConfigWindow()
    # app.exec_()
