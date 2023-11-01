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
from cooper_jacob_page import CooperJacobPage
from theis_recovery_page import TheisRecoveryPage
from about_us_page import AboutUsPage

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS WellData (
        Id INTEGER PRIMARY KEY,
        WellName TEXT UNIQUE,
        Location TEXT,
        Coordinates TEXT,
        Geology TEXT,
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
        self.setWindowTitle('AquaProbe-Beta1')
        self.well_table_obj=WellTablePage()
        self.prev_page_obj=PreviewPage()
        self.theis_page_obj=TheisPage()
        self.cooper_jacob_page_obj=CooperJacobPage()
        self.theis_recovery_page_obj=TheisRecoveryPage()
        try:
            self.well_table_obj.well_id_signal.connect(self.prev_page_obj.get_well)
            self.well_table_obj.well_id_signal.connect(self.theis_page_obj.get_well)
            self.well_table_obj.well_id_signal.connect(self.cooper_jacob_page_obj.get_well)
            self.well_table_obj.well_id_signal.connect(self.theis_recovery_page_obj.get_well)
        except Exception as e:
            print("Error connecting signal:", e)

        self.register_page(HomePage(),'homepage')
        self.register_page(self.well_table_obj,'welltable')
        self.register_page(self.prev_page_obj,'createwell')
        self.register_page(PreviewPage(),'preview')
        self.register_page(CreateWellPage(),'createwell')
        self.register_page(self.theis_page_obj,'theispage')
        self.register_page(self.cooper_jacob_page_obj,'cooperjacobpage')
        self.register_page(self.theis_recovery_page_obj,'theisrecoverypage')
        self.register_page(AboutUsPage(),'aboutus')
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
            if(name=='welltable'):
                self.well_table_obj.load_data_from_database()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MultiPageApp()
    main_app.show()
    sys.exit(app.exec_())
