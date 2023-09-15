from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5 import QtCore


class TheisPage(PageWindow,QObject):
    def __init__(self):
        super(TheisPage, self).__init__()
        uic.loadUi('theis.ui', self)
    
    @pyqtSlot(int)
    def get_well(self, row):
        print("Received theis row:", row)