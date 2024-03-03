from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
from PyQt5 import uic
from multiPageHandler import PageWindow


class HelpPage(PageWindow):
    def __init__(self):
        super(HelpPage, self).__init__()
        self.setup_ui()
        self.setWindowTitle("AquaProbe")
        self.set_statusbar_message("Version 1.0.0")
        self.add_copyright_label()
        self.setup_connections()

    def setup_ui(self):
        uic.loadUi("help.ui", self)

    def set_statusbar_message(self, message):
        self.statusbar.showMessage(message)

    def add_copyright_label(self):
        copyright_label = QLabel("Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.addPermanentWidget(copyright_label)

    def setup_connections(self):
        self.back_button.clicked.connect(self.go_back)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)

    def goto_aboutus(self):
        self.goto("aboutus")

    def goto_help(self):
        self.goto("helppage")

    def go_back(self):
        self.goto("homepage")
