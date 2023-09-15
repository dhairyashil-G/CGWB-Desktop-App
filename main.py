import sqlite3
import sys
from PyQt5 import QtCore
from multiPageHandler import PageWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from well_table import WellTablePage
from home_page import HomePage
from create_well import CreateWellPage
from preview import PreviewPage
from theis_page import TheisPage

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

        well_table_obj=WellTablePage()
        prev_page_obj=PreviewPage()
        theis_page_obj=TheisPage()
        try:
            well_table_obj.well_id_signal.connect(prev_page_obj.get_well)
            well_table_obj.well_id_signal.connect(theis_page_obj.get_well)
        except Exception as e:
            print("Error connecting signal:", e)

        self.register_page(HomePage(),'homepage')
        self.register_page(well_table_obj,'welltable')
        self.register_page(prev_page_obj,'createwell')
        self.register_page(PreviewPage(),'preview')
        self.register_page(theis_page_obj,'theispage')
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
