from PyQt5 import uic
from multiPageHandler import PageWindow
from well_table import WellTablePage
from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5 import QtCore


class PreviewPage(PageWindow,QObject):
    def __init__(self,*args,**kwargs):
        self.well_id=0

    def __init__(self):
        super(PreviewPage, self).__init__()
        uic.loadUi('preview.ui', self)
        self.back_button.clicked.connect(self.goback)
    
    @pyqtSlot(int)
    def get_well_id(self,well_id):
        self.well_id=well_id
        print("Received value in PageB:", well_id)

    def goback(self):
        self.goto('welltable') 
        try:
            print(self.well_id)
        except Exception as e:
            print(e)

