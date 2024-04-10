import os
import sqlite3
import json
import pandas as pd
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QLabel,
    QFileDialog,
    QMessageBox,
    QDateTimeEdit,
)
from PyQt5.QtCore import Qt, QDateTime
from multiPageHandler import PageWindow


class CreateWellPage(PageWindow):
    def __init__(self):
        super(CreateWellPage, self).__init__()
        uic.loadUi("create_well.ui", self)
        self.setWindowTitle("AquaProbe")
        self.statusbar.showMessage("Version 1.0.0")
        copyright_label = QLabel("Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.showMessage("Version 1.0.0")
        self.statusbar.addPermanentWidget(copyright_label)

        self.zones_list = []
        self.file_name = ""

        self.csv_button.clicked.connect(self.select_csv_file)
        self.save_button.clicked.connect(self.save_well_data)
        self.back_button.clicked.connect(self.goback)
        self.menuWellTable.aboutToShow.connect(self.goto_welltable)
        self.menuHome.aboutToShow.connect(self.goto_home)
        self.menuAbout.aboutToShow.connect(self.goto_aboutus)
        self.menuHelp.aboutToShow.connect(self.goto_help)
        self.zones_tapped_add_button.clicked.connect(self.add_zones_range)

        self.startdatetime_edit.setDateTime(QDateTime.currentDateTime())
        self.enddatetime_edit.setDateTime(QDateTime.currentDateTime())

    def goto_aboutus(self):
        self.goto("aboutus")

    def goto_home(self):
        self.goto("homepage")

    def goto_help(self):
        self.goto("helppage")

    def goto_welltable(self):
        self.goto("welltable")

    def add_zones_range(self):
        try:
            start_value = self.zones_tapped_start_spinbox.text()
            end_value = self.zones_tapped_end_spinbox.text()
            self.zones_list.append([start_value, end_value])
            self.updateTable()
            self.zones_tapped_start_spinbox.clear()
            self.zones_tapped_end_spinbox.clear()
        except ValueError:
            pass  # Ignore if the input is not a valid number

    def updateTable(self):
        num_ranges = len(self.zones_list)

        self.zones_tapped_table.setRowCount(num_ranges)

        for i, (start, end) in enumerate(self.zones_list):
            self.zones_tapped_table.setItem(i, 0, QTableWidgetItem(str(start)))
            self.zones_tapped_table.setItem(i, 1, QTableWidgetItem(str(end)))

    def is_csv_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == ".csv"

    def select_csv_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.file_name = ""
        self.file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
            options=options,
        )

        if self.file_name:
            QMessageBox.information(self, "Success", "Upload successful!")
            self.csv_button.setText(self.file_name)
        else:
            QMessageBox.information(self, "Error", "File not Uploaded!")

    def goback(self):
        self.goto("homepage")

    def save_well_data(self):

        if not are_all_fields_filled(self):
            QMessageBox.critical(self, "Error", "All fields are required!")

        elif self.startdatetime_edit.dateTime() > self.enddatetime_edit.dateTime():
            QMessageBox.critical(self, "Error", "Invalid datetime input!")

        elif self.is_csv_file(self.file_name) == False:
            QMessageBox.critical(self, "Error", "Invalid File type!")

        elif self.file_name == "":
            QMessageBox.critical(self, "Error", "CSV File not selected!")

        else:
            try:
                wellname = self.wellname_edit.text()
                location = self.location_edit.text()
                latitude = self.latitude_edit.text()
                longitude = self.longitude_edit.text()
                coordinates = "Latitude: " + latitude + "  Longitude: " + longitude
                geology = self.geology_edit.text()
                performedby = self.performedby_edit.text()
                startdatetime = self.startdatetime_edit.dateTime().toString(Qt.ISODate)
                enddatetime = self.enddatetime_edit.dateTime().toString(Qt.ISODate)
                current_datetime = QDateTime.currentDateTime().toString(Qt.ISODate)

                # Converting to datetime object to calculate the difference
                startdatetime_datetype = QDateTime.fromString(startdatetime, Qt.ISODate)
                enddatetime_datetype = QDateTime.fromString(enddatetime, Qt.ISODate)

                totalduration = startdatetime_datetype.secsTo(enddatetime_datetype)
                zonestappedstring = str(self.zones_list)
                zonestappedin = zonestappedstring
                welldepth = self.welldepth_spinbox.value()
                welldiameter = self.welldiameter_spinbox.value()
                staticwaterlevel = self.staticwaterlevel_spinbox.value()
                pumpingrate = self.pumpingrate_spinbox.value()
                distancefromwell = self.distancefromwell_spinbox.value()
                timepumpingstopped = self.timepumpingstopped_spinbox.value()
                csv_file_path = self.file_name

                try:
                    df = pd.read_csv(csv_file_path)
                except Exception as e:
                    print(f"Error reading csv file: {e}")

                    QMessageBox.critical(
                        None, "Error", "File not found at given location!"
                    )
                    self.loading_label.setText("")
                    self.goto("welltable")

                csv_file_data = {
                    # Assuming the first column is the 'time' column
                    "Time": df.iloc[:, 0].tolist(),
                    # Assuming the second column is the 'drawdown' column
                    "Drawdown": df.iloc[:, 1].tolist(),
                }

                json_csv_file_data = json.dumps(csv_file_data)

                # db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        """INSERT INTO WellData (WellName, Location, Coordinates, Geology, PerformedBy, CurrentDatetime, StartDatetime, EndDatetime, TotalDuration, ZonesTappedIn, WellDepth, WellDiameter, StaticWaterLevel, PumpingRate, DistanceFromWell, TimeWhenPumpingStopped, CsvFilePath, CsvFileData) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            wellname,
                            location,
                            coordinates,
                            geology,
                            performedby,
                            current_datetime,
                            startdatetime,
                            enddatetime,
                            totalduration,
                            zonestappedin,
                            welldepth,
                            welldiameter,
                            staticwaterlevel,
                            pumpingrate,
                            distancefromwell,
                            timepumpingstopped,
                            csv_file_path,
                            json_csv_file_data,
                        ),
                    )
                except sqlite3.Error as e:
                    print(f"Failed in create well query: {e}")

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
                # self.zonestappedin_spinbox.setValue(0)
                self.zones_tapped_table.clearContents()
                self.welldepth_spinbox.setValue(0)
                self.welldiameter_spinbox.setValue(0)
                self.staticwaterlevel_spinbox.setValue(0)
                self.pumpingrate_spinbox.setValue(0)
                self.timepumpingstopped_spinbox.setValue(0)
                self.distancefromwell_spinbox.setValue(0)
                self.file_name = ""
                self.csv_button.setText("Open File Explorer")
                self.zones_list = []
                self.geology_edit.clear()

                self.goto("welltable")
            except Exception as e:
                QMessageBox.critical(self, "Error", "Well creation unsuccessful!")


def are_all_fields_filled(self):
    required_fields = [
        self.wellname_edit.text(),
        self.location_edit.text(),
        self.latitude_edit.text(),
        self.longitude_edit.text(),
        self.geology_edit.text(),
        self.performedby_edit.text(),
        self.file_name,
    ]
    for field in required_fields:
        if not field:
            return False
    return True
