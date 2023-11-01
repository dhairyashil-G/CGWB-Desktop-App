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
from datetime import datetime

class TheisPage(PageWindow,QObject):
    def __init__(self):
        super(TheisPage, self).__init__()
        TheisPage.well_id_global=None
        TheisPage.pdf_obj=None
        uic.loadUi('theis.ui', self)
        self.setWindowTitle('AquaProbe-Beta1.1')
        self.update_button.clicked.connect(self.calculate_theis)
        self.back_button.clicked.connect(self.goback)
        self.download_report_button.clicked.connect(self.create_report)

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
            self.adjust_storativity.setValue(S)
            self.adjust_transmissivity.setValue(T)
        else:
            S=self.adjust_storativity.value()
            T=self.adjust_transmissivity.value()

        u = self.calculate_u(r, S, T, t)
        wu = exp1(u)
        one_by_u = 1/u

        # rms_residual = np.sqrt(np.sum((wu - s)**2))

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

        self.transmissivity_value.setText(str(round(T,3)))
        self.storativity_value.setText("{:.3f}".format(S))
        # self.rms_residual_value.setText(str(round(rms_residual,3)))


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
        pdf.cell(0, 10, 'Theis Test Report', align='C', ln=1)
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
            f" Start Datetime: {startdatetime} ")
        lst2.append(
            f" End Datetime: {enddatetime} ")
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
        pdf.cell(0, 10, f'Storativity : {"{:.3f}".format(S)}', ln=1)
        # pdf.cell(0, 10, f'RMS Residual : {round(rms_residual, 3)}%', ln=1)
        pdf.ln(5)

        pdf.dashed_line(10, int(pdf.get_y()), 210 - 10,
                        int(pdf.get_y()), dash_length=1, space_length=1)
        TheisPage.pdf_obj=pdf


    def create_report(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Theis Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
        if(file_path):
            TheisPage.pdf_obj.output(f'{file_path}')