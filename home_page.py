from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5 import uic
from multiPageHandler import PageWindow


class HomePage(PageWindow):
    def __init__(self):
        super(HomePage,self).__init__()
        uic.loadUi('home_page.ui',self)

        self.welltable_button.clicked.connect(self.goto_welltable)
        self.createwell_button.clicked.connect(self.goto_createwell)

    def goto_welltable(self):
        self.goto('welltable')

    def goto_createwell(self):
        self.goto('createwell')


