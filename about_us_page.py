from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5 import uic
from multiPageHandler import PageWindow

class AboutUsPage(PageWindow):
    def __init__(self):
        super(AboutUsPage,self).__init__()
        uic.loadUi('about_us.ui',self)
        self.setWindowTitle('AquaProbe')
        self.statusbar.showMessage("Version 1.0.0")
        self.back_button.clicked.connect(self.goback)
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

    def goback(self):
        self.goto('homepage')