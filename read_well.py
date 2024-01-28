import os
from PyQt5 import QtCore
import sqlite3
import csv
from datetime import datetime
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5 import uic
from multiPageHandler import PageWindow
import pandas as pd
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
        ReadWellPage.show_data_button_flag=False

        self.back_button.clicked.connect(self.goback)
        self.refill_button.clicked.connect(self.refill)
        self.edit_button.clicked.connect(self.goedit)
        self.save_csv_file.clicked.connect(self.savecsv)
        self.menuWellTable.aboutToShow.connect(self.goto_welltable)
        self.menuHome.aboutToShow.connect(self.goto_home)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)

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
        ReadWellPage.show_data_button_flag=True
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
        self.welldepth_spinbox.setValue(well_object.get('WellDepth'))
        self.welldiameter_spinbox.setValue(well_object.get('WellDiameter'))
        self.staticwaterlevel_spinbox.setValue(well_object.get('StaticWaterLevel'))
        self.pumpingrate_spinbox.setValue(well_object.get('PumpingRate'))
        self.timepumpingstopped_spinbox.setValue(well_object.get('TimeWhenPumpingStopped'))
        self.distancefromwell_spinbox.setValue(well_object.get('DistanceFromWell'))
        self.file_name=well_object.get('CsvFilePath')
        self.geology_edit.setText(well_object.get('Geology'))
        zones_tapped_list=eval(well_object.get('ZonesTappedIn'))

        self.csv_file_data_dict=eval(well_object.get('CsvFileData'))
        
        self.save_csv_file.setEnabled(True)

        zones_tapped_df = pd.DataFrame(zones_tapped_list, columns=['start', 'end'])
        model = PandasModel(zones_tapped_df)
        self.zones_tapped.setModel(model)

        # CSV File Data can be rendered in a table view----------
        # csv_data_df=pd.DataFrame(csv_file_data_dict)
        # model1 = PandasModel(csv_data_df)
        # self.csv_file_data.setModel(model1)
        # ----------------------------------------------------------

    def is_csv_file(self,file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == ".csv"

    def goback(self):
        self.goto('welltable')
        self.save_csv_file.setEnabled(False)
        ReadWellPage.show_data_button_flag=False
    
   
    def goedit(self):
        self.well_id_signal.emit(int(ReadWellPage.well_id_global))
        # print("Next button clicked for row:", row)
        self.goto('updatewell')
    
    def savecsv(self):
        if(ReadWellPage.show_data_button_flag==False):
            QMessageBox.information(self, 'Error', 'Please click on show data button!')
        else:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
            
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"CSV Data {formatted_datetime}", "CSV Files (*.csv)", options=options)
            
            if file_path:
                data=self.csv_file_data_dict  
                
                with open(file_path, 'w', newline='') as csvfile:
                    fieldnames = ['Time', 'Drawdown']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for i in range(len(data['Time'])):
                        writer.writerow({'Time': data['Time'][i], 'Drawdown': data['Drawdown'][i]})
                
                QMessageBox.information(self, 'Success', 'Report saved successfully!')