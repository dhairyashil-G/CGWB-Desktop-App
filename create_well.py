import os
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit,QSpinBox, QPushButton, QComboBox, QDateTimeEdit,QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal,QDateTime
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5 import uic
from multiPageHandler import PageWindow
class CreateWellPage(PageWindow):
    def __init__(self):
        super(CreateWellPage,self).__init__()
        uic.loadUi('create_well.ui',self)
        self.setWindowTitle('AquaProbe-Beta1.1')

        self.csv_button.clicked.connect(self.select_csv_file)
        self.save_button.clicked.connect(self.save_well_data)
        self.back_button.clicked.connect(self.goback)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)

    def goto_aboutus(self):
        self.goto('aboutus')

    def goto_help(self):
        self.goto('helppage')

    def is_csv_file(self,file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == ".csv"

    def select_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.file_name=''
        self.file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if self.file_name:
            QMessageBox.information(self, 'Success', 'Upload successful!')
            print("Selected CSV File:", self.file_name)


    def goback(self):
        self.goto('homepage')
   
    
    def save_well_data(self):

        if(self.startdatetime_edit.dateTime()>self.enddatetime_edit.dateTime()):
            QMessageBox.critical(self, 'Error', 'Invalid datetime input!')

        elif(self.is_csv_file(self.file_name)==False):
            QMessageBox.critical(self, 'Error', 'Invalid File type!')

        elif(self.file_name==''):
            QMessageBox.critical(self, 'Error', 'CSV File not selected!')


        else:
            try:
                wellname = self.wellname_edit.text()
                location = self.location_edit.text()
                latitude=self.latitude_edit.text()
                longitude=self.longitude_edit.text()
                coordinates = "Latitude: "+latitude+"  Longitude: "+longitude
                geology = self.geology_edit.text()
                performedby = self.performedby_edit.text()
                startdatetime = self.startdatetime_edit.dateTime().toString(Qt.ISODate)
                enddatetime = self.enddatetime_edit.dateTime().toString(Qt.ISODate)
                current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)
                
                # Converting to datetime object to calculate the difference
                startdatetime_datetype = QDateTime.fromString(startdatetime, Qt.ISODate)
                enddatetime_datetype = QDateTime.fromString(enddatetime, Qt.ISODate)

                
                totalduration = startdatetime_datetype.secsTo(enddatetime_datetype)
                zonestappedin = self.zonestappedin_spinbox.value()
                welldepth = self.welldepth_spinbox.value()
                welldiameter = self.welldiameter_spinbox.value()
                staticwaterlevel = self.staticwaterlevel_spinbox.value()
                pumpingrate = self.pumpingrate_spinbox.value()
                distancefromwell = self.distancefromwell_spinbox.value()
                timepumpingstopped=self.timepumpingstopped_spinbox.value()
                csv_file_path = self.file_name
                

                # db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
                conn = sqlite3.connect('./database.db')
                cursor = conn.cursor()
                try:
                    cursor.execute(f'''INSERT INTO WellData (WellName, Location, Coordinates, Geology, PerformedBy, CurrentDatetime, StartDatetime, EndDatetime, TotalDuration, ZonesTappedIn, WellDepth, WellDiameter, StaticWaterLevel, PumpingRate, DistanceFromWell,TimeWhenPumpingStopped, CsvFilePath) 
                    VALUES ('{wellname}', '{location}', '{coordinates}', '{geology}', '{performedby}', '{current_datetime}', '{startdatetime}', '{enddatetime}', {totalduration}, {zonestappedin}, {welldepth}, {welldiameter}, {staticwaterlevel}, {pumpingrate}, {distancefromwell}, {timepumpingstopped}, '{csv_file_path}')''')
                except sqlite3.Error as e:
                    print("SQLite error:", e)
                    print("Failed to execute query with values:")

                conn.commit()
                conn.close()
                # Clear input fields after saving
                self.wellname_edit.clear()
                self.location_edit.clear()
                self.latitude_edit.clear()
                self.longitude_edit.clear()
                self.performedby_edit.clear()
                self.startdatetime_edit.setDateTime(QDateTime.currentDateTime())
                self.enddatetime_edit.setDateTime(QDateTime.currentDateTime())
                self.zonestappedin_spinbox.setValue(0)
                self.welldepth_spinbox.setValue(0)
                self.welldiameter_spinbox.setValue(0)
                self.staticwaterlevel_spinbox.setValue(0)
                self.pumpingrate_spinbox.setValue(0)
                self.timepumpingstopped_spinbox.setValue(0)
                self.distancefromwell_spinbox.setValue(0)
                self.geology_edit.clear()
                self.goto('welltable')
            except Exception as e:
                QMessageBox.critical(self, 'Error', 'Well creation unsuccessful!')

