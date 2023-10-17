from PyQt5 import uic
from PyQt5.QtWidgets import QScrollArea,QWidget
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
import pandas as pd
import plotly.graph_objs as go
import sqlite3
import numpy as np
import math

class CooperJacobPage(PageWindow,QObject):
    def __init__(self):
        super(CooperJacobPage, self).__init__()
         # Create a scroll area to contain the entire window's content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Create a widget to hold all the window's content
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)

        # Set the scroll area as the central widget of the main window
        self.setCentralWidget(self.scroll_area)
        uic.loadUi('cooper_jacob.ui', self)
        CooperJacobPage.well_id_global=None
        self.back_button.clicked.connect(self.goback)
        # self.calculate_cooper_jacob()
        self.plot_button.clicked.connect(self.calculate_cooper_jacob)
    
    @pyqtSlot(int)
    def get_well(self, row):
        CooperJacobPage.well_id_global=row

    def goback(self):
        self.goto('preview')

    def calculate_cooper_jacob(self):

        well_id = CooperJacobPage.well_id_global 
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

        x_data = np.array(df['Time'])
        y_data = np.array(df['Drawdown'])

        if(self.adjust_slope.value()==0 and self.adjust_x_intercept.value()==0):
            print('if block')
            slope, y_intercept = np.polyfit(np.log(x_data), y_data, 1)
            x_intercept = np.exp((-y_intercept)/slope)
            self.adjust_slope.setValue(round(slope,6))
            self.adjust_x_intercept.setValue(round(x_intercept,6))
        else:
            slope=self.adjust_slope.value()
            x_intercept=self.adjust_x_intercept.value()


        y_intercept = ((-slope)*np.log(x_intercept))


        delta_s = abs((slope*math.log(100) + y_intercept) -
                    (slope*math.log(10) + y_intercept))
        t_0 = np.exp((-y_intercept)/slope)

        T = (2.303*Q)/(4*math.pi*delta_s)
        S = (2.25*T*(t_0/1440)) / (r*r)

        self.transmissivity_value.setText(str(T))
        self.storativity_value.setText(str(S))
        
        t_for_u = (r*r * S)/(4*T*0.05)*1440

        self.show_plot(x_data,y_data,y_intercept,slope)

    def show_plot(self,x_data,y_data,y_intercept,slope):
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
        xaxis_title="log Time (min)",
        yaxis_title="Drawdown (m)",
        legend_title="Legend"
        )

        self.graph_container.setHtml(fig.to_html(include_plotlyjs='cdn'))
