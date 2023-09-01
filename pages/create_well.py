import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit,QSpinBox, QPushButton, QComboBox, QDateTimeEdit,QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal,QDateTime
from PyQt5.QtWidgets import QFileDialog,QGridLayout

class CreateWellPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Create Well Page')
        self.setGeometry(100, 100, 800, 600)  # Adjust the window size

        # Create a scroll area
        scroll_area = QScrollArea()
        main_widget = QWidget()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)
        self.setCentralWidget(scroll_area)

        # Create a main layout
        main_layout = QVBoxLayout(main_widget)

        # Create a grid layout for the form with two columns
        form_layout = QGridLayout()
        main_layout.addLayout(form_layout)

        # Left column
        left_column = QVBoxLayout()
        form_layout.addLayout(left_column, 0, 0)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.go_back_to_homepage)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        left_column.addWidget(QLabel('Well Name:'))
        left_column.addWidget(QLabel('Location:'))
        left_column.addWidget(QLabel('Coordinates:'))
        left_column.addWidget(QLabel('Soil Type:'))
        left_column.addWidget(QLabel('Lithology:'))
        left_column.addWidget(QLabel('Performed By:'))
        left_column.addWidget(QLabel('Well Depth:'))
        left_column.addWidget(QLabel('Well Diameter:'))
        left_column.addWidget(QLabel('Static Water Level:'))
        left_column.addWidget(QLabel('Pumping Rate:'))
        left_column.addWidget(QLabel('Distance from Well:'))
        left_column.addWidget(QLabel('Start Datetime:'))
        left_column.addWidget(QLabel('End Datetime:'))
        left_column.addWidget(QLabel('Total Duration (minutes):'))
        left_column.addWidget(QLabel('Time When Pumping Stopped (minutes):'))
        left_column.addWidget(QLabel('Zones Tapped In:'))
        left_column.addWidget(QLabel('Select CSV File'))

        # Right column
        right_column = QVBoxLayout()
        form_layout.addLayout(right_column, 0, 1)

        self.wellname_edit=QLineEdit()
        right_column.addWidget(self.wellname_edit)

        self.location_edit=QLineEdit()
        right_column.addWidget(self.location_edit)

        self.coordinates_edit=QLineEdit()
        right_column.addWidget(self.coordinates_edit)

        self.soiltype_combo = QComboBox()
        self.soiltype_combo.addItems(['Alluvial Soil', 'Red and Yellow Soil', 'Black Cotton Soil', 'Laterite Soil', 'Mountainous or Forest Soil', 'Arid or Desert Soil', 'Saline and Alkaline Soil', 'Peaty and Marshy Soil'])
        right_column.addWidget(self.soiltype_combo)
        
        self.lithology_combo = QComboBox()
        self.lithology_combo.addItems(['Evaporitic', 'Carbonated', 'Detrital', 'Non consolidated', 'Plutonic', 'Volcanic', 'Metamorphic', 'Ortogneissic'])
        right_column.addWidget(self.lithology_combo)
        
        self.performedby_edit=QLineEdit()
        right_column.addWidget(self.performedby_edit)
        
        self.welldepth_spinbox=QSpinBox()
        right_column.addWidget(self.welldepth_spinbox)
        
        self.welldiameter_spinbox=QSpinBox()
        right_column.addWidget(self.welldiameter_spinbox)
        
        self.staticwaterlevel_spinbox=QSpinBox()
        right_column.addWidget(self.staticwaterlevel_spinbox)
        
        self.pumpingrate_spinbox=QSpinBox()
        right_column.addWidget(self.pumpingrate_spinbox)
        
        self.distancefromwell_spinbox=QSpinBox()
        right_column.addWidget(self.distancefromwell_spinbox)
        
        self.startdatetime_edit=QDateTimeEdit()
        right_column.addWidget(self.startdatetime_edit)
        
        self.enddatetime_edit=QDateTimeEdit()
        right_column.addWidget(self.enddatetime_edit)
        
        self.totalduration_spinbox=QSpinBox()
        right_column.addWidget(self.totalduration_spinbox)
        
        self.timepumpingstopped_spinbox=QSpinBox()
        right_column.addWidget(self.timepumpingstopped_spinbox)
        
        self.zonestappedin_spinbox=QSpinBox()
        right_column.addWidget(self.zonestappedin_spinbox)
        
        self.csv_button=QPushButton('Open',self)
        self.csv_button.clicked.connect(self.select_csv_file)
        right_column.addWidget(self.csv_button)
           

        # Create a button to save the well data
        self.save_button = QPushButton('Save Well Data')
        main_layout.addWidget(self.save_button)

        # Connect signals and slots
        self.save_button.clicked.connect(self.save_well_data)
        # ... (other signal connections)

    def select_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if self.file_name:
            print("Selected CSV File:", self.file_name)


    def go_back_to_homepage(self):
        self.parent().show_home_page()
        
    
    def save_well_data(self):
        wellname = self.wellname_edit.text()
        location = self.location_edit.text()
        coordinates = self.coordinates_edit.text()
        soiltype = self.soiltype_combo.currentText()
        lithology = self.lithology_combo.currentText()
        performedby = self.performedby_edit.text()
        startdatetime = self.startdatetime_edit.dateTime().toString(Qt.ISODate)
        enddatetime = self.enddatetime_edit.dateTime().toString(Qt.ISODate)
        current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
        totalduration = self.totalduration_spinbox.value()
        zonestappedin = self.zonestappedin_spinbox.value()
        welldepth = self.welldepth_spinbox.value()
        welldiameter = self.welldiameter_spinbox.value()
        staticwaterlevel = self.staticwaterlevel_spinbox.value()
        pumpingrate = self.pumpingrate_spinbox.value()
        distancefromwell = self.distancefromwell_spinbox.value()
        timepumpingstopped=self.timepumpingstopped_spinbox.value()
        csv_file_path = self.file_name
        
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''INSERT INTO WellData (WellName, Location, Coordinates, SoilType, Lithology, PerformedBy, CurrentDatetime, StartDatetime, EndDatetime, TotalDuration, ZonesTappedIn, WellDepth, WellDiameter, StaticWaterLevel, PumpingRate, DistanceFromWell,TimeWhenPumpingStopped, CsvFilePath) 
            VALUES ('{wellname}', '{location}', '{coordinates}', '{soiltype}', '{lithology}', '{performedby}', '{current_datetime}', '{startdatetime}', '{enddatetime}', {totalduration}, {zonestappedin}, {welldepth}, {welldiameter}, {staticwaterlevel}, {pumpingrate}, {distancefromwell}, {timepumpingstopped}, '{csv_file_path}')''')
        except sqlite3.Error as e:
            print("SQLite error:", e)
            print("Failed to execute query with values:")

        conn.commit()
        conn.close()
        # self.data_saved_signal.emit()
        # Clear input fields after saving
        self.wellname_edit.clear()
        self.location_edit.clear()
        self.coordinates_edit.clear()
        self.performedby_edit.clear()
        self.startdatetime_edit.setDateTime(QDateTime.currentDateTime())
        self.enddatetime_edit.setDateTime(QDateTime.currentDateTime())
        self.totalduration_spinbox.setValue(0)
        self.zonestappedin_spinbox.setValue(0)
        self.welldepth_spinbox.setValue(0)
        self.welldiameter_spinbox.setValue(0)
        self.staticwaterlevel_spinbox.setValue(0)
        self.pumpingrate_spinbox.setValue(0)
        self.distancefromwell_spinbox.setValue(0)