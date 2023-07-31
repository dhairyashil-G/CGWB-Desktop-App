import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from pages.home_page import HomePage
import sqlite3

class MultiPageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.home_page = HomePage()
        # self.settings_page = SettingsPage()

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self.home_page)
        # self.stacked_widget.addWidget(self.settings_page)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.current_page = self.home_page

    def set_page(self, page):
        self.stacked_widget.setCurrentWidget(page)
        self.current_page = page


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MultiPageApp()
    main_app.setWindowTitle('AquaProbe')
    main_app.setWindowState(Qt.WindowMaximized)
    main_app.show()


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
            TimeWhenPumpingStopped INTEGER
        );
        ''')
    conn.commit()
    conn.close()

    sys.exit(app.exec_())