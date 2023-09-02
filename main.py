import sqlite3
import sys
from PyQt5 import QtCore
from multiPageHandler import PageWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget
from well_table import WellTablePage
from home_page import HomePage
from create_well import CreateWellPage

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS WellData (
        Id INTEGER PRIMARY KEY,
        WellName TEXT UNIQUE,
        Location TEXT,
        Coordinates TEXT,
        SoilType TEXT CHECK(SoilType IN ('Alluvial Soil', 'Red and Yellow Soil', 'Black Cotton Soil', 'Laterite Soil', 'Mountainous or Forest Soil','Arid or Desert Soil','Saline and Alkaline Soil','Peaty and Marshy Soil')),
        Lithology TEXT CHECK(Lithology IN ('Evaporitic', 'Carbonated', 'Detrital', 'Non consolidated', 'Plutonic','Volcanic','Metamorphic','Ortogneissic')),
        PerformedBy TEXT,
        CurrentDatetime TIMESTAMP,
        StartDatetime TIMESTAMP,
        EndDatetime TIMESTAMP,
        TotalDuration INTEGER,
        ZonesTappedIn INTEGER,
        WellDepth INTEGER,
        WellDiameter INTEGER,
        StaticWaterLevel INTEGER,
        PumpingRate INTEGER,
        DistanceFromWell INTEGER,
        TimeWhenPumpingStopped INTEGER,
        CsvFilePath TEXT  
    );
    ''')
class MultiPageApp(QMainWindow):
    def __init__(self):
        super(MultiPageApp ,self).__init__()

        self.stacked_widget=QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pages={}

        self.register_page(HomePage(),'homepage')
        self.register_page(WellTablePage(),'welltable')
        self.register_page(CreateWellPage(),'createwell')
        self.goto('homepage')

    def register_page(self,page,name):
        self.pages[name]=page
        self.stacked_widget.addWidget(page)

        if isinstance(page,PageWindow):
            page.gotoSignal.connect(self.goto)

    @QtCore.pyqtSlot(str)
    def goto(self,name):
        if name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[name])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MultiPageApp()
    main_app.show()
    sys.exit(app.exec_())
