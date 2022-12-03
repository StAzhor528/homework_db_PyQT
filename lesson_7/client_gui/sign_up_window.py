from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
from PyQt5.QtCore import QEvent


class SignUpDialog(QDialog):
    """Окно регистрации пользователя."""
    def __init__(self):
        super().__init__()
        self.ok_pressed = False

        self.setWindowTitle('Окно регистрации')
        self.setFixedSize(230, 210)
        self.input_name_label = QLabel('Введите имя пользователя', self)
        self.input_name_label.move(40, 10)
        self.input_name_label.setFixedSize(220, 20)

        self.input_name = QLineEdit(self)
        self.input_name.setFixedSize(210, 27)
        self.input_name.move(10, 30)

        self.input_password_label = QLabel('Введите пароль', self)
        self.input_password_label.move(70, 60)
        self.input_password_label.setFixedSize(220, 20)

        self.input_password = QLineEdit(self)
        self.input_password.setFixedSize(210, 27)
        self.input_password.move(10, 80)

        self.input_repeat_password_label = QLabel('Повторите пароль', self)
        self.input_repeat_password_label.move(70, 110)
        self.input_repeat_password_label.setFixedSize(220, 20)

        self.input_repeat_password = QLineEdit(self)
        self.input_repeat_password.setFixedSize(210, 27)
        self.input_repeat_password.move(10, 130)

        self.ok_btn = QPushButton('Ok', self)
        self.ok_btn.setFixedSize(60, 30)
        self.ok_btn.move(10, 170)
        self.ok_btn.clicked.connect(self.click)

        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.setFixedSize(70, 30)
        self.cancel_btn.move(151, 170)
        self.cancel_btn.clicked.connect(qApp.exit)



    def click(self):
        """Подтверждает корректность введенных данных и закрывает окно."""
        if self.input_name.text() and self.input_password.text() \
                and self.input_repeat_password_label.text() \
                and self.input_password.text() == self.input_repeat_password.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = SignUpDialog()
    app.exec_()