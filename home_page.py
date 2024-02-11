from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

class HomePage(PageWindow):
    def __init__(self):
        super(HomePage,self).__init__()
        uic.loadUi('home_page.ui',self)
        self.setWindowTitle('AquaProbe')
        copyright_label = QLabel("Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.showMessage("Version 1.0.0")
        self.statusbar.addPermanentWidget(copyright_label)


        self.createwell_button.clicked.connect(self.goto_createwell)
        self.welltable_button.clicked.connect(self.goto_welltable)
        self.menuWellTable.aboutToShow.connect(self.goto_welltable)
        self.menuHome.aboutToShow.connect(self.goto_home)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)
        self.tabWidget.setCurrentIndex(0)
        
        self.images = [QPixmap('Home_image1.gif'),
                       QPixmap('carousel_images/C0.jpg'), 
                       QPixmap('carousel_images/C1.jpg'), 
                       QPixmap('carousel_images/C2.jpg'), 
                       QPixmap('carousel_images/C3.jpg'), 
                       QPixmap('carousel_images/C4.jpg'),
                       QPixmap('carousel_images/C5.jpg'),   
                    ]
        
        self.currentIndex = 0

        self.carousel_images_label.setPixmap(self.images[self.currentIndex])

        self.carousel_prev_button.clicked.connect(self.previousImage)

        self.carousel_next_button.clicked.connect(self.nextImage)

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

    def previousImage(self):
        self.currentIndex -= 1
        if self.currentIndex < 0:
            self.currentIndex = len(self.images) - 1
        self.carousel_images_label.setPixmap(self.images[self.currentIndex])

    def nextImage(self):
        self.currentIndex += 1
        if self.currentIndex >= len(self.images):
            self.currentIndex = 0
        self.carousel_images_label.setPixmap(self.images[self.currentIndex])

