from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
from PyQt5.QtCore import QEvent

class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ok_pressed = False

        self.setWindowTitle('Привет')
        self.setFixedSize(230, 120)
        self.input_name_label = QLabel('Введите имя пользователя', self)
        self.input_name_label.move(40, 10)
        self.input_name_label.setFixedSize(220, 20)

        self.input_name = QLineEdit(self)
        self.input_name.setFixedSize(210, 27)
        self.input_name.move(10, 30)

        self.ok_btn = QPushButton('OK', self)
        self.ok_btn.move(10, 80)
        self.ok_btn.clicked.connect(self.click)

        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.move(127, 80)
        self.cancel_btn.clicked.connect(qApp.exit)

        self.show()

    def click(self):
        if self.input_name.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()