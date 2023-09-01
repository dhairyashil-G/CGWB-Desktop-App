# from PyQt5 import QtWidgets, uic
# import sys

# class Ui(QtWidgets.QMainWindow):
#     def __init__(self):
#         super(Ui, self).__init__()
#         uic.loadUi('pages/home.ui', self)
#         self.show()

# app = QtWidgets.QApplication(sys.argv)
# window = Ui()
# app.exec_()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.well_table_button = QPushButton('Open Well Table')
        self.create_well_button=QPushButton('Create Well')
        layout.addWidget(self.well_table_button)
        layout.addWidget(self.create_well_button)
        self.setLayout(layout)

