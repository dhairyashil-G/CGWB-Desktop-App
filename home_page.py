from PyQt5 import uic, QtCore
from multiPageHandler import PageWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox


class HomePage(PageWindow):
    def __init__(self):
        super(HomePage, self).__init__()
        uic.loadUi("home_page.ui", self)
        self.setWindowTitle("AquaProbe")
        self.setup_status_bar()
        self.setup_navigation()
        self.setup_carousel()

    def setup_status_bar(self):
        copyright_label = QLabel("Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.showMessage("Version 1.0.0")
        self.statusbar.addPermanentWidget(copyright_label)

    def setup_navigation(self):
        self.createwell_button.clicked.connect(self.goto_createwell)
        self.welltable_button.clicked.connect(self.goto_welltable)
        self.menuWellTable.aboutToShow.connect(self.goto_welltable)
        self.review_terms_button.clicked.connect(self.show_terms_of_use)
        self.menuHome.aboutToShow.connect(self.goto_home)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)
        self.tabWidget.setCurrentIndex(0)

    def setup_carousel(self):
        self.images = [
            QPixmap("flowchart.svg"),
            QPixmap("Home_image1.gif"),
            QPixmap("carousel_images/C0.jpg"),
            QPixmap("carousel_images/C1.jpg"),
            QPixmap("carousel_images/C2.jpg"),
            QPixmap("carousel_images/C3.jpg"),
            QPixmap("carousel_images/C4.jpg"),
            QPixmap("carousel_images/C5.jpg"),
        ]
        self.currentIndex = 0
        self.carousel_images_label.setPixmap(self.images[self.currentIndex])
        # self.carousel_prev_button.clicked.connect(self.previous_image)
        # self.carousel_next_button.clicked.connect(self.next_image)

    def goto_aboutus(self):
        self.goto("aboutus")

    def goto_home(self):
        self.goto("homepage")

    def goto_help(self):
        self.goto("helppage")

    def goto_welltable(self):
        self.goto("welltable")

    def goto_createwell(self):
        self.goto("createwell")

    def previous_image(self):
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = len(self.images) - 1
        self.carousel_images_label.setPixmap(self.images[self.currentIndex])

    def next_image(self):
        self.currentIndex += 1
        if self.currentIndex >= len(self.images):
            self.currentIndex = 0
        self.carousel_images_label.setPixmap(self.images[self.currentIndex])

    def show_terms_of_use(self):
        terms_text = """
        <html><head/><body><p>
        <b>Terms of Use</b><br><br>
        Please read the terms carefully before using the AquaProbe application. By downloading, installing, or using the Software, you agree to be bound by these terms. If you do not agree to these terms, do not use the Software.<br><br>
        
        <b>License:</b> The Software is provided as a freeware under a non-exclusive, non-transferable license to use it solely for personal or internal use purposes. You may not sublicense, sell, or distribute the software without prior written consent.<br><br>
        
        <b>Restrictions:</b> You may not modify, adapt, translate, reverse engineer, decompile, disassemble, or create derivative works based on the software.<br><br>
        
        <b>Ownership:</b> All rights, title, and interest in and to the Software, including any updates, enhancements, or modifications, remain with team members (SIH2022-BV798) and CGWB, Department of Water Resources, River Development and Ganga Rejuvenation, Ministry of Jal Shakti.<br><br>
        
        <b>Changes to Terms:</b> AquaProbe (SIH2022-BV798) reserves the right to change these terms at any time without notice. Your continued use of the Software after any such changes constitutes your acceptance of the new terms.<br><br>
        
        <b>Citation:</b> The use of the software may be cited as follows - Gidwani, S., & Ghatage, D. (2024). AquaProbe: A Desktop Application for Water Analysis. Developed under SIH 2022. Central Ground Water Board (CGWB), Ministry of Jal Shakti, Govt of India.<br><br>
        
        By using the Software, you acknowledge that you have read and understood these terms and agree to be bound by them. If you have any questions about these terms, please contact us at <a href="mailto:aquaprobe.help@gmail.com">aquaprobe.help@gmail.com</a>.
        </p></body></html>
        """
        msgBox = QMessageBox()
        msgBox.setTextFormat(1)  # Rich text format
        msgBox.setText(terms_text)
        msgBox.setWindowTitle("Terms of Use")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.exec()
