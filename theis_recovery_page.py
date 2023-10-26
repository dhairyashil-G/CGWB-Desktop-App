from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5.QtWidgets import QFileDialog
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from scipy.special import exp1
import pandas as pd
import numpy as np
from fpdf import FPDF
import os
import math
from datetime import datetime

class TheisRecoveryPage(PageWindow,QObject):
    def __init__(self):
        super(TheisRecoveryPage, self).__init__()
        TheisRecoveryPage.well_id_global=None
        TheisRecoveryPage.pdf_obj=None
        uic.loadUi('theis_recovery.ui', self)
        self.plot_button.clicked.connect(self.calculate_theis_recovery)
        self.back_button.clicked.connect(self.goback)
        # self.download_report_button.clicked.connect(self.create_report)

    @pyqtSlot(int)
    def get_well(self, row):
        TheisRecoveryPage.well_id_global=row

    def goback(self):
        self.goto('preview')

    def calculate_theis_recovery(self):
        well_id = TheisRecoveryPage.well_id_global 
        # print(f'IN showPlot : {well_id}')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
        row = cursor.fetchone()

        well_object = {}
        if row:
            column_names = [desc[0] for desc in cursor.description]
            for i in range(len(column_names)):
                well_object[column_names[i]] = row[i]


        print(well_object)
        Q = well_object.get('PumpingRate')
        r = well_object.get('DistanceFromWell')
        t_when_pumping_stopped = well_object.get('TimeWhenPumpingStopped')
        csv_file_url = well_object.get('CsvFilePath')
        df = pd.read_csv(csv_file_url)

        df = df.loc[df['Time'] > t_when_pumping_stopped]
        df['Time'] = df['Time']-t_when_pumping_stopped
        df.rename(columns={'Time': 't_dash',
                'Drawdown': 'Residual_Drawdown'}, inplace=True)
        df['t'] = df['t_dash']+t_when_pumping_stopped
        df['t_by_t_dash'] = df['t']/df['t_dash']
        df = df[['t', 't_dash', 't_by_t_dash', 'Residual_Drawdown']]

        x_data = np.array(df['t_by_t_dash'])
        y_data = np.array(df['Residual_Drawdown'])

        if(self.adjust_slope.value()==0 and self.adjust_x_intercept.value()==0):
            print('if block')
            slope, y_intercept = np.polyfit(np.log(x_data), y_data, 1)
            x_intercept = np.exp((-y_intercept)/slope)
            self.adjust_slope.setValue(round(slope,6))
            self.adjust_x_intercept.setValue(round(x_intercept,6))
        else:
            slope=self.adjust_slope.value()
            x_intercept=self.adjust_x_intercept.value()
            print('custom slope and x intercept found')

        y_intercept = ((-slope)*np.log(x_intercept))
        delta_s_dash = abs((slope*math.log(100) + y_intercept) -
                        (slope*math.log(10) + y_intercept))

        T = (2.303*Q)/(4*math.pi*delta_s_dash)

        ratio_of_S = np.exp((-y_intercept)/slope)

        df = df.round(decimals=3)
        self.transmissivity_value.setText(str(round(T,3)))
        self.delta_s_value.setText("{:.3f}".format(delta_s_dash))
        self.relative_change_s_value.setText(str(round(ratio_of_S,3)))


        fig = go.Figure()

        fig.add_trace(go.Scatter(x=x_data, y=y_data,
                                mode='lines+markers',
                                name='Actual Data'))
        fig.update_xaxes(type="log")

        fig.add_trace(go.Scatter(x=np.exp((y_data - y_intercept)/slope), y=y_data,
                                mode='lines+markers',
                                name='Fitting Line'))
        fig.update_xaxes(type="log")

        fig.update_layout(
            title="Drawdown vs Time",
            xaxis_title="log t/t'",
            yaxis_title="Residual Drawdown (m)",
            legend_title="Legend"
        )
        self.graph_container.setHtml(fig.to_html(include_plotlyjs='cdn'))
        

