from PyQt5 import uic,QtWebEngineWidgets
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject, pyqtSlot
import sqlite3
import pandas as pd
import plotly.graph_objs as go

class PreviewPage(PageWindow, QObject):
    def __init__(self):
        super(PreviewPage, self).__init__()
        uic.loadUi('preview.ui', self)
        self.back_button.clicked.connect(self.goback)
        self.theis_button.clicked.connect(self.gotheis)
        well_id_global=None
        self.plot_button.clicked.connect(self.show_plot)

    def show_plot(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()


        well_id = PreviewPage.well_id_global 
        # print(f'IN showPlot : {well_id}')


        cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
        row = cursor.fetchone()

        well_object = {}

        if row:
            column_names = [desc[0] for desc in cursor.description]
            for i in range(len(column_names)):
                well_object[column_names[i]] = row[i]
        
        # print(well_object)


        t_when_pumping_stopped = well_object.get('TimeWhenPumpingStopped', 0)
        # t_when_pumping_stopped = 240
        csv_file_url = well_object.get('CsvFilePath', '')
        df = pd.read_csv(csv_file_url)
        df_pumping_test = df[df['Time'] <= t_when_pumping_stopped]
        df_recovery_test = df[df['Time'] > t_when_pumping_stopped]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_pumping_test['Time'], y=df_pumping_test['Drawdown'],
                                 mode='lines+markers',
                                 name='Pumping Data',
                                 line=dict(color='blue'), 
                                 marker=dict(color='blue') 
                                 ))
        fig.update_xaxes(type="log")
        fig.add_trace(go.Scatter(x=df_recovery_test['Time'], y=df_recovery_test['Drawdown'],
                                 mode='lines+markers',
                                 name='Recovery Data'))
        fig.update_xaxes(type="log")
        fig.update_layout(
            title="Drawdown vs Time",
            xaxis_title="log Time (min)",
            yaxis_title="Drawdown (m)",
            legend_title="Legend"
        )
        
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def goback(self):
        self.goto('welltable') 

    def gotheis(self):
        self.goto('theispage')

    @pyqtSlot(int)
    def get_well(self, row):
        PreviewPage.well_id_global=row
        self.show_plot()
        