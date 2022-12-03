from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
from PyQt5.QtCore import QEvent

from client_gui.sign_up_window import SignUpDialog


class UserNameDialog(QDialog):
    """Окно авторизации для входа в приложение."""
    def __init__(self):
        super().__init__()
        self.auth = False
        self.reg = False
        self.name_pass = None
        self.name_pass_reg = None

        self.setWindowTitle('Привет')
        self.setFixedSize(230, 170)
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

        self.ok_btn = QPushButton('Sign in', self)
        self.ok_btn.setFixedSize(60, 30)
        self.ok_btn.move(10, 120)
        self.ok_btn.clicked.connect(self.click)

        self.register_btn = QPushButton('Sign up', self)
        self.register_btn.setFixedSize(60, 30)
        self.register_btn.move(80, 120)
        self.register_btn.clicked.connect(self.reg_user)

        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.setFixedSize(70, 30)
        self.cancel_btn.move(151, 120)
        self.cancel_btn.clicked.connect(qApp.exit)


    def click(self):
        """Пытается авторизоваться с введенными данными."""
        if self.input_name.text() and self.input_password.text():
            self.auth = True
            qApp.exit()
            self.name_pass = self.input_name.text(), self.input_password.text()
            self.close()

    def reg_user(self):
        """Переходит к окну регистрации."""
        self.reg_window = SignUpDialog()
        self.reg_window.show()
        self.reg_window.exec_()
        self.name_pass_reg = self.reg_window.input_name.text(), self.reg_window.input_password.text()
        self.reg = self.reg_window.ok_pressed
        self.close()

if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    dial.show()
    app.exec_()



