from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5 import QtCore
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from scipy.special import exp1
import pandas as pd
import numpy as np

class TheisPage(PageWindow,QObject):
    def __init__(self):
        super(TheisPage, self).__init__()
        TheisPage.well_id_global=None
        TheisPage.pdf_obj=None
        uic.loadUi('theis.ui', self)
        self.update_button.clicked.connect(self.calculate_theis)
        self.back_button.clicked.connect(self.goback)
    
    @pyqtSlot(int)
    def get_well(self, row):
        TheisPage.well_id_global=row

    def goback(self):
        self.goto('preview')

    def get_S_and_T(self, m, c, Q, r):
        Tfit = Q / 4 / np.pi / m
        Sfit = 4 * Tfit / r**2 * np.exp(-(c/m + np.euler_gamma))
        return Sfit, Tfit
    
    def calculate_u(self, r, S, T, t):
        return (r*r*S)/(4*T*t)

    def calculate_theis(self):
        well_id = TheisPage.well_id_global 
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

        # recovery_df = df.loc[df['Time'] > t_when_pumping_stopped]
        df = df.loc[df['Time'] <= t_when_pumping_stopped]
        s = np.array(df['Drawdown'])
        t = np.array(df['Time'])
        
        t_by_r2 = np.divide(t, (r*r))
        t = np.divide(t, 1440)

        lnt = np.log(t)
        coeffs = np.polyfit(np.log(t), s, 1)
        m, c = coeffs

        if(self.adjust_storativity.value()==0 and self.adjust_transmissivity.value()==0):
            S_calc, T_calc = self.get_S_and_T(m, c, Q, r)
            S = S_calc
            T = T_calc
        else:
            S=self.adjust_storativity.value()
            T=self.adjust_transmissivity.value()

        u = self.calculate_u(r, S, T, t)
        wu = exp1(u)
        one_by_u = 1/u

        rms_residual = np.sqrt(np.sum((wu - s)**2))

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.update_layout(
            xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'top'}, yaxis_domain=[0, 0.94])

        fig.add_trace(go.Scatter(x=one_by_u, y=wu, mode='lines',
                                name='Well Function'), secondary_y=False)
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

        # fig.add_trace(go.Scatter(x=t_by_r2, y=s, mode='lines',
        #                          name="Drawdown vs t/r2"), secondary_y=True)
        fig.add_trace(go.Scatter(x=t_by_r2, y=s, mode='lines',
                                name="Drawdown vs t"), secondary_y=True)
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

        fig.data[1].update(xaxis='x2')

        fig.update_layout(title="Drawdown vs Time", xaxis_title="log Time (min)",
            yaxis_title="log Drawdown (m)",
            legend_title="Legend")

        self.graph_container.setHtml(fig.to_html(include_plotlyjs='cdn'))