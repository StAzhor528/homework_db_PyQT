from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class DelContactDialog(QDialog):
    def __init__(self, database, username):
        super().__init__()
        self.db = database
        self.username = username

        self.setFixedSize(280, 100)
        self.setWindowTitle('Выбор контакта для удаления')

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для удаления', self)
        self.selector_label.setFixedSize(260, 20)
        self.selector_label.move(40, 5)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(260, 20)
        self.selector.move(10, 30)

        self.refresh_btn = QPushButton('Обновить', self)
        self.refresh_btn.setFixedSize(80, 30)
        self.refresh_btn.move(10, 60)

        self.del_btn = QPushButton('Удалить', self)
        self.del_btn.setFixedSize(80, 30)
        self.del_btn.move(100, 60)

        self.cancel_btn = QPushButton('Отмена', self)
        self.cancel_btn.setFixedSize(80, 30)
        self.cancel_btn.move(190, 60)
        self.cancel_btn.clicked.connect(self.close)

        self.client_contacts(self.username)
        self.refresh_btn.clicked.connect(self.client_contacts)

    def client_contacts(self, username):
        self.selector.clear()
        contact_list = self.db.get_my_contacts(username)
        self.selector.addItems(contact_list)


if __name__ == '__main__':
    app = QApplication([])
    dial = DelContactDialog()
    app.exec_()