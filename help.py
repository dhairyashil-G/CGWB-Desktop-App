from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
from PyQt5 import uic
from multiPageHandler import PageWindow

class HelpPage(PageWindow):
    def __init__(self):
        super(HelpPage,self).__init__()
        uic.loadUi('help.ui',self)
        self.setWindowTitle('AquaProbe')
        self.statusbar.showMessage("Version 1.0.0")
        copyright_label = QLabel("Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.showMessage("Version 1.0.0")
        self.statusbar.addPermanentWidget(copyright_label)

        self.back_button.clicked.connect(self.goback)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)
    
    def goto_aboutus(self):
        self.goto('aboutus')

    def goto_help(self):
        self.goto('helppage')

    def goback(self):
        self.goto('homepage')