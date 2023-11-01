from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5 import uic
from multiPageHandler import PageWindow

class AboutUsPage(PageWindow):
    def __init__(self):
        super(AboutUsPage,self).__init__()
        uic.loadUi('about_us.ui',self)
        self.setWindowTitle('AquaProbe-Beta1')
        self.back_button.clicked.connect(self.goback)

    def goback(self):
        self.goto('homepage')