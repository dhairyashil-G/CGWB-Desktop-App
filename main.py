import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QStackedWidget
from pages.well_table import WellTablePage
from pages.home_page import HomePage
from pages.create_well import CreateWellPage

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
        super().__init__()

        self.setWindowTitle('MultiPage App')
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Create a stacked widget to manage pages
        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)

        # Create and add pages to the stacked widget
        self.home_page = HomePage()
        self.well_table_page = WellTablePage()
        self.create_well_page=CreateWellPage()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.well_table_page)
        self.stacked_widget.addWidget(self.create_well_page)

        # Connect buttons to switch pages
        self.home_page.well_table_button.clicked.connect(self.show_well_table_page)
        self.home_page.create_well_button.clicked.connect(self.show_create_well_page)

        self.current_page = self.home_page

    def show_home_page(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.current_page = self.home_page

    def show_well_table_page(self):
        self.stacked_widget.setCurrentWidget(self.well_table_page)
        self.current_page = self.well_table_page

    def show_create_well_page(self):
        self.stacked_widget.setCurrentWidget(self.create_well_page)
        self.current_page = self.create_well_page

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MultiPageApp()
    main_app.show()
    sys.exit(app.exec_())

if(sys.exit(app.exec_())):
    conn.commit()
    conn.close()