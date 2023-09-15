from PyQt5 import uic,QtWidgets, QtWebEngineWidgets
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5 import QtCore

import sqlite3
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio


class PreviewPage(PageWindow,QObject):
    def __init__(self):
        super(PreviewPage, self).__init__()
        uic.loadUi('preview.ui', self)
        self.back_button.clicked.connect(self.goback)
        self.theis_button.clicked.connect(self.gotheis)
        self.well_id=None

    def goback(self):
        self.goto('welltable') 

    def gotheis(self):
        self.goto('theispage')

    # def show_graph(self,well_id):
    #     # Replace 'database.db' with your database file name
    #     conn = sqlite3.connect('database.db')
    #     cursor = conn.cursor()

    #     # Define the well_id you want to fetch
    #     #   # Replace with the desired well_id

    #     # Fetch selected columns for the well with the specified Id
    #     cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
    #     row = cursor.fetchone()

    #     # Initialize an empty dictionary to store the data
    #     well_object = {}

    #     if row:
    #         # Extract the column names from the cursor description
    #         column_names = [desc[0] for desc in cursor.description]

    #         # Populate the dictionary with column names as keys and corresponding values
    #         for i in range(len(column_names)):
    #             well_object[column_names[i]] = row[i]

    #     print(well_object)
        

    @pyqtSlot(int)
    def get_well(self, row):
        # Replace 'database.db' with your database file name
         # Connect to the SQLite database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Define the well_id you want to fetch (replace with your desired well_id)
        well_id = row  # Replace with the desired well_id

        # Fetch selected columns for the well with the specified Id
        cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
        row = cursor.fetchone()

        # Initialize an empty dictionary to store the data
        well_object = {}

        if row:
            # Extract the column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Populate the dictionary with column names as keys and corresponding values
            for i in range(len(column_names)):
                well_object[column_names[i]] = row[i]

        # Fetch data from the well_object
        t_when_pumping_stopped = well_object.get('TimeWhenPumpingStopped', 0)
        csv_file_url = well_object.get('CsvFilePath', '')

        # Fetch data from the CSV file
        df = pd.read_csv(csv_file_url)
        df_pumping_test = df[df['Time'] <= t_when_pumping_stopped]
        df_recovery_test = df[df['Time'] > t_when_pumping_stopped]
        print(df_pumping_test)
        print(df_recovery_test)
