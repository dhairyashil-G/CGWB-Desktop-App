from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5 import uic
from multiPageHandler import PageWindow



class HomePage(PageWindow):
    def __init__(self):
        super(HomePage,self).__init__()
        uic.loadUi('home_page.ui',self)
        self.setWindowTitle('AquaProbe-Beta1.1')


        self.createwell_button.clicked.connect(self.goto_createwell)
        self.welltable_button.clicked.connect(self.goto_welltable)
        self.menuWellTable.aboutToShow.connect(self.goto_welltable)
        self.menuHome.aboutToShow.connect(self.goto_home)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)

    def goto_aboutus(self):
        self.goto('aboutus')

    def goto_home(self):
        self.goto('homepage')

    def goto_help(self):
        self.goto('helppage')

    def goto_welltable(self):
        self.goto('welltable')


    def goto_createwell(self):
        self.goto('createwell')


