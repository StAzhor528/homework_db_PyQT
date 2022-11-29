import time
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView, QHBoxLayout, QWidget, QListWidget, \
    QListWidgetItem, QPushButton, QVBoxLayout, QTextEdit, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSlot, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from client_gui.add_contact_gui import AddContactDialog
from errors import ServerError


class ClientMainWindow(QMainWindow):
    def __init__(self, database, transport):
        super().__init__()
        self.db = database
        self.transport = transport
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Чат')
        self.setFixedSize(600, 600)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.horizontal_layout = QHBoxLayout(self.centralwidget)

        # Список контактов и кнопки добавления, обновления и удаления.
        self.left_layout = QVBoxLayout()
        self.contacts_list_label = QLabel('Список контактов', self)
        self.contacts_list = QListWidget()

        self.refresh_btn = QPushButton('Обновить', self)
        self.del_btn = QPushButton('Удалить', self)
        self.add_btn = QPushButton('Добавить', self)
        self.bth_left_layout = QHBoxLayout()
        self.bth_left_layout.addWidget(self.refresh_btn)
        self.bth_left_layout.addWidget(self.del_btn)
        self.bth_left_layout.addWidget(self.add_btn)

        self.left_layout.addWidget(self.contacts_list_label)
        self.left_layout.addWidget(self.contacts_list)
        self.left_layout.addLayout(self.bth_left_layout)

        # Чат, окно набора сообщения и кнопка отправить.

        self.right_layout = QVBoxLayout()
        self.messages_list_label = QLabel('Окно чата', self)
        self.messages_list = QListView()
        self.messages_list.setWordWrap(True)




        self.text_msg_label = QLabel('Введите сообщение', self)
        self.text_msg = QTextEdit()
        self.text_msg.setDisabled(True)
        self.bth_right_layout = QHBoxLayout()
        self.clear_btn = QPushButton('Очистить окно', self)
        self.clear_btn.setDisabled(True)
        self.send_btn = QPushButton('Отправить', self)
        self.send_btn.setDisabled(True)
        self.bth_right_layout.addWidget(self.clear_btn)
        self.bth_right_layout.addWidget(self.send_btn)

        self.right_layout.addWidget(self.messages_list_label)
        self.right_layout.addWidget(self.messages_list)
        self.right_layout.addWidget(self.text_msg_label)
        self.right_layout.addWidget(self.text_msg)
        self.right_layout.addLayout(self.bth_right_layout)

        self.horizontal_layout.addLayout(self.left_layout)
        self.horizontal_layout.addLayout(self.right_layout)

        # Дополнительные требующиеся атрибуты
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None

        # Действие кнопки "Обновить".
        self.refresh_btn.clicked.connect(lambda: self.refresh_contacts(self.transport.name))
        # Действие кнопки "Удалить".
        self.del_btn.clicked.connect(self.del_contacts)
        # Действие кнопки "Добавить".
        self.add_btn.clicked.connect(lambda: self.add_contact_window(self.db, self.transport.name))

        # Двойной клик по имени пользователя
        self.contacts_list.doubleClicked.connect(self.select_active_user)

        # Действие кнопки "Очистить окно".
        self.clear_btn.clicked.connect(self.clear_message_window)

        # Действие кнопки "Отправить".
        self.send_btn.clicked.connect(self.send_message)


        self.refresh_contacts(self.transport.name)
        self.show()

    def refresh_contacts(self, username):
        self.contacts_list.clear()
        contact_list = self.db.get_my_contacts(username)
        self.contacts_list.addItems(contact_list)

    def add_contact_window(self, db, username):
        add_dialog = AddContactDialog(db, username)
        add_dialog.add_btn.clicked.connect(lambda: self.add_contact_action(add_dialog))
        add_dialog.show()

    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(self.transport.name, new_contact)
        item.close()

    def add_contact(self, username, new_contact):
        self.db.insert_in_contactdb(username, new_contact, '', str(datetime.now()))
        self.refresh_contacts(username)

    def del_contacts(self):
        try:
            name_for_del = self.contacts_list.currentItem().text()
            if name_for_del:
                self.db.del_in_contactdb(self.transport.name, name_for_del)
                self.refresh_contacts(self.transport.name)
                return
        except Exception:
            self.messages.warning(self, 'Ошибка', 'Вы не выбрали клиента')




    def select_active_user(self):
        # Выбранный пользователем (даблклик) находится в выделеном элементе в QListView
        self.current_chat = self.contacts_list.currentIndex().data()

        # вызываем основную функцию
        self.set_active_user()

    def set_active_user(self):
        # активируем кнопки
        self.clear_btn.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.text_msg.setDisabled(False)

        # Заполняем окно историю сообщений по требуемому пользователю.
        self.history_list_update()

    def history_list_update(self):
        msg_list = sorted(self.db.get_all_users_messages(self.current_chat), key=lambda item: item[3])

        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.messages_list.setModel(self.history_model)
        # Очистим от старых записей
        self.history_model.clear()

        # Берём не более 20 последних записей.
        messages_list_length = len(msg_list)
        start_index = 0
        if messages_list_length > 20:
            start_index = messages_list_length - 20
        # Заполнение модели записями, так-же стоит разделить входящие и исходящие выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for i in range(start_index, messages_list_length):
            item = msg_list[i]
            if item[2]:
                if item[0] == self.current_chat and item[1] == self.transport.name:
                    mess = QStandardItem(f'Входящее от {item[0]}:\n {item[2]}')
                    mess.setEditable(False)
                    mess.setBackground(QBrush(QColor(255, 213, 213)))
                    mess.setTextAlignment(Qt.AlignLeft)
                    self.history_model.appendRow(mess)
                elif item[1] == self.current_chat and item[0] == self.transport.name:
                    mess = QStandardItem(f'Исходящее от {item[0]}:\n {item[2]}')
                    mess.setEditable(False)
                    mess.setTextAlignment(Qt.AlignRight)
                    mess.setBackground(QBrush(QColor(204, 255, 204)))
                    self.history_model.appendRow(mess)

        self.messages_list.scrollToBottom()

    def clear_message_window(self):
        self.text_msg.clear()

    def send_message(self):
        # Текст в поле, проверяем что поле не пустое затем забирается сообщение и поле очищается
        message_text = self.text_msg.toPlainText()
        self.text_msg.clear()
        if not message_text:
            return
        try:
            self.transport.send_message(self.transport.name, self.current_chat, message_text)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.history_list_update()


    @pyqtSlot(str)
    def message(self, sender):
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Проверим есть ли такой пользователь у нас в контактах:
            if sender in self.db.get_my_contacts(self.transport.name):
                # Если есть, спрашиваем и желании открыть с ним чат и открываем при желании
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}, открыть чат с ним?', QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # Раз нету,спрашиваем хотим ли добавить юзера в контакты.
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}.\n Данного пользователя нет в вашем контакт-листе.\n Добавить в контакты и открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(self.transport.name, sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'Сбой соединения', 'Потеряно соединение с сервером. ')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    main_window = ClientMainWindow()
    main_window.show()
    app.exec_()
