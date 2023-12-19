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
        self.setWindowTitle('AquaProbe-Beta1.1')
        self.plot_button.clicked.connect(self.calculate_theis_recovery)
        self.back_button.clicked.connect(self.goback)
        self.download_report_button.clicked.connect(self.create_report)

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
        
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font('Arial', 'B', 10)
        pdf.image('logo.jpg', x=10, y=10, w=25, h=30)
        pdf.image('aquaprobe_logo.png',
                x=pdf.w-60, y=10, w=50, h=25)
        pdf.cell(0, 30, '', ln=1)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, 'CENTRAL GROUND WATER BOARD (CGWB)', ln=1)
        pdf.ln(5)

        pdf.set_font('Arial', 'BU', 18)
        pdf.cell(0, 10, 'Cooper Jacob Test Report', align='C', ln=1)
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)
        lst1 = list()
        lst2 = list()
        lst1.append(f"Well Name: {well_object.get('WellName')}" )
        lst2.append(f"Performed By: {well_object.get('PerformedBy')}")
        lst1.append(f"Location: {well_object.get('Location')}")
        lst2.append(f"Coordinates: {well_object.get('Coordinates')}")
        startdatetime=well_object.get('StartDatetime').replace('T',' ')
        enddatetime=well_object.get('EndDatetime').replace('T',' ')
        lst1.append(
            f"Start Datetime: {startdatetime} ")
        lst2.append(
            f"End Datetime: {enddatetime} ")
        lst1.append(
            f"Duration Of Pumping Test: {well_object.get('TimeWhenPumpingStopped')} min")
        lst2.append(f"Geology:  {well_object.get('Geology')}")
        lst1.append(f"Zones Tapped: {well_object.get('ZonesTappedIn')} bgl-m")
        lst2.append(f"Static Water Level:  {well_object.get('StaticWaterLevel')} m")
        lst1.append(f"Well Depth: {well_object.get('WellDepth')} m")
        lst2.append(f"Well Diameter:  {well_object.get('WellDiameter')} m")
        lst1.append(f"Pumping Rate: {well_object.get('PumpingRate')} m3/day")
        lst2.append(f"Distance from Well:  {well_object.get('DistanceFromWell')} m")
        
        pdf.set_font("Arial", "", 12)
        col_width = pdf.w / 2.2
        for item1, item2 in zip(lst1, lst2):
            pdf.cell(col_width, 10, item1, border=1)
            pdf.cell(col_width, 10, item2, border=1)
            pdf.ln(10)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, "Graphical Interpretation", ln=1)
        fig.write_image("fig.png")
        pdf.image('fig.png', w=200, h=150)
        os.remove("fig.png")
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Transmissivity : {round(T, 3)} m2/day', ln=1)
        pdf.cell(0, 10, f'delta S : {round(delta_s_dash,3)}', ln=1)
        pdf.cell(0, 10, f'Relative Change in S = {round(ratio_of_S, 3)}%', ln=1)
        pdf.ln(5)

        pdf.dashed_line(10, int(pdf.get_y()), 210 - 10,
                        int(pdf.get_y()), dash_length=1, space_length=1)
        TheisRecoveryPage.pdf_obj=pdf
    
    def create_report(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Theis Recovery Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
        print(file_path)
        if(file_path):
            TheisRecoveryPage.pdf_obj.output(f'{file_path}')