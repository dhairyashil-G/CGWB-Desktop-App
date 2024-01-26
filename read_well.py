import os
from PyQt5 import QtCore
import sqlite3
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5 import uic
from multiPageHandler import PageWindow
import pandas as pd
import json
import re
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

Qt = QtCore.Qt

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[section])
    
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.iloc[index.row()][index.column()]))
        return QtCore.QVariant()

class ReadWellPage(PageWindow,QObject):
    well_id_signal = pyqtSignal(int)
    def __init__(self):
        super(ReadWellPage,self).__init__()
        uic.loadUi('read_well.ui',self)
        self.setWindowTitle('AquaProbe-Beta1.1')

        ReadWellPage.well_id_global=None


        self.back_button.clicked.connect(self.goback)
        self.refill_button.clicked.connect(self.refill)
        self.edit_button.clicked.connect(self.goedit)
        # self.menuWellTable.aboutToShow.connect(self.goto_welltable)
        # self.menuHome.aboutToShow.connect(self.goto_home)
        # self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        # self.menuHelp.aboutToShow.connect(self.goto_help)

    def goto_aboutus(self):
        self.goto('aboutus')

    def goto_home(self):
        self.goto('homepage')

    def goto_help(self):
        self.goto('helppage')

    def goto_welltable(self):
        self.goto('welltable')

    @pyqtSlot(int)
    def get_well(self, row):
        ReadWellPage.well_id_global=row
        print('row received')
    
    def refill(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        well_id = ReadWellPage.well_id_global
    
        # print(f'IN showPlot : {well_id}')


        cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
        row = cursor.fetchone()
        # Populate the input widgets with the fetched values
        well_object = {}

        if row:
            column_names = [desc[0] for desc in cursor.description]
            for i in range(len(column_names)):
                well_object[column_names[i]] = row[i]    
        
        self.wellname_edit.setText(well_object.get('WellName'))
        self.location_edit.setText(well_object.get('Location'))
        coordinates=well_object.get('Coordinates').split()

        latitude = coordinates[1]
        longitude = coordinates[3]
        self.latitude_edit.setText(latitude)
        self.longitude_edit.setText(longitude)
        self.performedby_edit.setText(well_object.get('PerformedBy'))
        self.startdatetime_edit.setDateTime(QDateTime.fromString(well_object.get('StartDatetime'), 'yyyy-MM-dd hh:mm:ss'))
        self.enddatetime_edit.setDateTime(QDateTime.fromString(well_object.get('EndDatetime'), 'yyyy-MM-dd hh:mm:ss'))
        # Additional fields need to be filled similarly

        # Filling the rest of the fields
        # self.zones_tapped_table.setRowCount(1)  # Assuming 1 row for simplicity
        # self.zones_tapped_table.setItem(0, 0, QTableWidgetItem(str(zonestappedin)))
        self.welldepth_spinbox.setValue(well_object.get('WellDepth'))
        self.welldiameter_spinbox.setValue(well_object.get('WellDiameter'))
        self.staticwaterlevel_spinbox.setValue(well_object.get('StaticWaterLevel'))
        self.pumpingrate_spinbox.setValue(well_object.get('PumpingRate'))
        self.timepumpingstopped_spinbox.setValue(well_object.get('TimeWhenPumpingStopped'))
        self.distancefromwell_spinbox.setValue(well_object.get('DistanceFromWell'))
        self.csv_button.setText(well_object.get('CsvFilePath'))
        self.file_name=well_object.get('CsvFilePath')
        self.geology_edit.setText(well_object.get('Geology'))
        zones_tapped_list=eval(well_object.get('ZonesTappedIn'))
        prev_zones_data=''
        for zones in zones_tapped_list:
            prev_zones_data+=f'-    {zones[0]}-{zones[1]}\n'
        
        self.zones_tapped_prev_data.setText(prev_zones_data)
        csv_file_data_dict=eval(well_object.get('CsvFileData'))
        csv_data_df=pd.DataFrame(csv_file_data_dict)

        model1 = PandasModel(csv_data_df)
        self.csv_file_data.setModel(model1)

    def is_csv_file(self,file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == ".csv"

    def goback(self):
        self.goto('homepage')
   
    def goedit(self):
        self.well_id_signal.emit(int(ReadWellPage.well_id_global))
        # print("Next button clicked for row:", row)
        self.goto('updatewell')