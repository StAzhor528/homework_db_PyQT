from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView, QHBoxLayout, QWidget, QListWidget, \
    QListWidgetItem, QPushButton, QVBoxLayout, QTextEdit, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSlot, QEvent
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor

class Test(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(600, 600)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.layout = QHBoxLayout(self.centralwidget)
        self.messages = QMessageBox()

        self.view = QListView()
        self.view.setWordWrap(True)
        self.model = QStandardItemModel()
        self.view.setModel(self.model)
        mess = QStandardItem('sjdvhbah kjs dks snwjd ns nldn sldn lsd lskd lksmdlksm lksm dlksm skdm\n ;sdkm ;dskm ;skmd ;dskm ;sk m')
        mess.setEditable(False)
        mess.setBackground(QBrush(QColor(255, 213, 213)))
        mess.setTextAlignment(Qt.AlignLeft)
        self.model.appendRow(mess)
        self.btn = QPushButton('Ok', self)

        self.layout.addWidget(self.view)
        self.layout.addWidget(self.btn)

        # self.btn.clicked.connect(self.del_item)
        self.show()


    # def del_item(self):
    #     item_name = self.lst.currentItem().text()
    #     self.data.remove(item_name)
    #     self.lst.clear()
    #     self.lst.addItems(self.data)
    #     self.messages.information(self, 'afa', 'AWDA')


if __name__ == '__main__':
    app = QApplication([])
    test = Test()
    app.exec_()

#
# test_lst = [('a', 1), ('d', 4), ('b', 2), ('c', 3)]
# lst = sorted(test_lst, key=lambda item: item[0])
# print(lst)

