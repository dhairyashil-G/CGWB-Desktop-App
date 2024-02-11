from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot,pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QApplication,QLabel
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from scipy.special import exp1
import pandas as pd
import numpy as np
from fpdf import FPDF
import os
from datetime import datetime
import plotly.io as pio

class TheisPage(PageWindow,QObject):
    theis_analyzed=pyqtSignal(bool)
    theis_signal_data=pyqtSignal(dict)

    def __init__(self):
        super(TheisPage, self).__init__()
        TheisPage.well_id_global=None
        TheisPage.pdf_obj=None
        TheisPage.start_time=0
        TheisPage.end_time=0
        uic.loadUi('theis.ui', self)
        self.setWindowTitle('AquaProbe')
        self.statusbar.showMessage("Version 1.0.0")
        copyright_label = QLabel("Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.showMessage("Version 1.0.0")
        self.statusbar.addPermanentWidget(copyright_label)

        self.plot_button.clicked.connect(self.calculate_theis)
        self.back_button.clicked.connect(self.goback)
        self.download_report_button.clicked.connect(self.create_report)
        self.adjust_start_time.valueChanged.connect(self.start_time_changed)
        self.adjust_end_time.valueChanged.connect(self.end_time_changed)
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
        TheisPage.well_id_global=row

    @pyqtSlot(float)
    def start_time_changed(self,value):
        TheisPage.start_time=value
        self.adjust_storativity.setValue(0)
        self.adjust_transmissivity.setValue(0)
    
    @pyqtSlot(float)
    def end_time_changed(self,value):
        TheisPage.end_time=value
        self.adjust_storativity.setValue(0)
        self.adjust_transmissivity.setValue(0)

    def goback(self):
        self.goto('preview')

    def get_S_and_T(self, m, c, Q, r):
        Tfit = Q / 4 / np.pi / m
        Sfit = 4 * Tfit / r**2 * np.exp(-(c/m + np.euler_gamma))
        return Sfit, Tfit
    
    def calculate_u(self, r, S, T, t):
        return (r*r*S)/(4*T*t)

    def calculate_theis(self):
        self.loading_label.setText('Please wait...This might take some time...')
        QApplication.processEvents()
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
        t_when_pumping_stopped_org = well_object.get('TimeWhenPumpingStopped')
       
        csv_file_data = well_object.get('CsvFileData')
        dict_csv_data=eval(csv_file_data)
        df_org = pd.DataFrame(dict_csv_data)
        df = pd.DataFrame(dict_csv_data)     

        if(self.adjust_start_time.value()==0 and self.adjust_end_time.value()==0):
            start_time = df['Time'].iloc[0]
            end_time = t_when_pumping_stopped
            print("point 1")
            self.adjust_start_time.setValue(start_time)
            self.adjust_end_time.setValue(end_time)
            TheisPage.start_time=start_time
            TheisPage.end_time=end_time

        df = df.loc[(TheisPage.start_time <= df['Time']) & (df['Time'] <= TheisPage.end_time)]

        df_org = df_org.loc[(df_org['Time'] <= t_when_pumping_stopped_org)]
        s_org = np.array(df_org['Drawdown'])
        t_org = np.array(df_org['Time'])
        t_by_r2_org = np.divide(t_org, (r*r))

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

        fig.update_layout(xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'top'}, yaxis_domain=[0, 0.94])

        fig.add_trace(go.Scatter(x=one_by_u, y=wu, mode='lines+markers',
                                name='Well Function'), secondary_y=False)
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

        fig.add_trace(go.Scatter(x=t_by_r2_org, y=s_org, mode='lines+markers',
                                name="Actual Data"), secondary_y=True)
        fig.data[1].update(xaxis='x2')

        fig.add_trace(go.Scatter(x=t_by_r2, y=s, mode='lines+markers',
                                name="Selected Data"), secondary_y=True)
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")

        fig.data[2].update(xaxis='x2')

        fig.update_layout(
            title="Method: Theis", 
            xaxis_title="log Time (min)",
            yaxis_title="log Drawdown (m)",
            legend_title="Legend",
            title_x=0.5,
            xaxis=dict(rangeslider=dict(visible=True))
        )
        fig.update_layout(
            annotations=[
                dict(
                    text="Time Vs Drawdown",
                    x=0.56,
                    y=1.1,
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    font=dict(size=14),
                )
            ]
        )
        self.graph_container.setHtml(fig.to_html(include_plotlyjs='cdn'))   

        self.transmissivity_value.setText(str(round(T,3)))
        self.storativity_value.setText("{:.8f}".format(S))
        # self.rms_residual_value.setText(str(round(rms_residual,3)))


        pdf = FPDF()
        pdf.add_page()

        pdf.set_font('Arial', 'B', 10)
        pdf.image('logo.png', x=10, y=10, w=25, h=30)
        pdf.image('aquaprobe_logo.png',
                x=pdf.w-60, y=10, w=50, h=25)
        pdf.cell(0, 30, '', ln=1)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 10, 'CENTRAL GROUND WATER BOARD (CGWB)', ln=1)
        pdf.ln(5)

        pdf.set_font('Arial', 'BU', 18)
        pdf.cell(0, 10, 'Theis Test Report', align='C', ln=1)
        pdf.ln(10)

        pdf.set_font('Arial', '', 12)
        lst1 = list()
        lst2 = list()
        lst1.append(f"Well Name: {well_object.get('WellName')}" )
        lst2.append(f"Performed By: {well_object.get('PerformedBy')}")
        lst1.append(f"Location: {well_object.get('Location')}")
        lst2.append(f"{well_object.get('Coordinates')}")
        startdatetime=well_object.get('StartDatetime').replace('T',' ')
        enddatetime=well_object.get('EndDatetime').replace('T',' ')
        lst1.append(
            f"Start Datetime: {startdatetime} ")
        lst2.append(
            f"End Datetime: {enddatetime} ")
        lst1.append(
            f"Duration Of Pumping Test: {well_object.get('TimeWhenPumpingStopped')} min")
        lst2.append(f"Geology: {well_object.get('Geology')}")
        zones_list=eval(well_object.get('ZonesTappedIn'))
        lst1.append(f"Number of Zones Tapped: {len(zones_list)}")
        lst2.append(f"Static Water Level: {well_object.get('StaticWaterLevel')} m-bgl")
        lst1.append(f"Well Depth: {well_object.get('WellDepth')} m")
        lst2.append(f"Well Diameter: {well_object.get('WellDiameter')} m")
        lst1.append(f"Pumping Rate: {well_object.get('PumpingRate')} m³/day")
        lst2.append(f"Distance from Well: {well_object.get('DistanceFromWell')} m")
        pdf.set_font("Arial", "", 12)
        col_width = pdf.w / 2.2
        for item1, item2 in zip(lst1, lst2):
            pdf.cell(col_width, 10, item1, border=1)
            pdf.cell(col_width, 10, item2, border=1)
            pdf.ln(10)
        pdf.ln(5)

        pdf.cell(0,10,"Zones Tapped:",ln=1)
        lst5=list()
        lst6=list()
        lst5.append("Start (m)")
        lst6.append("End (m)")
        for zones in zones_list:
            lst5.append(f"{zones[0]}")
            lst6.append(f"{zones[1]}")
        
        for item1, item2 in zip(lst5, lst6):
            pdf.cell(20, 10, item1, border=1)
            pdf.cell(20, 10, item2, border=1)
            pdf.ln(10)
        pdf.ln(5)

        pdf.cell(0,10,"Test Parameters:",ln=1)
        lst3=list()
        lst4=list()
        lst3.append(f"Analysis Start Time: {TheisPage.start_time} min")
        lst4.append(f"Analysis End Time: {TheisPage.end_time} min")
        # If more parameters come in future just add them to these lists
        for item1, item2 in zip(lst3, lst4):
            pdf.cell(col_width, 10, item1, border=1)
            pdf.cell(col_width, 10, item2, border=1)
            pdf.ln(10)
        pdf.ln(5)
        
        pdf.add_page()
        pdf.ln(15)
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, "Graphical Interpretation", ln=1)
        fig.write_image("fig.png")
        pdf.image('fig.png', w=200, h=150)
        os.remove("fig.png")
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Transmissivity : {round(T, 3)} m²/day', ln=1)
        pdf.cell(0, 10, f'Storativity : {"{:.8f}".format(S)}', ln=1)
        # pdf.cell(0, 10, f'RMS Residual : {round(rms_residual, 3)}%', ln=1)
        pdf.ln(5)

        TheisPage.pdf_obj=pdf
        self.loading_label.setText('')
        self.theis_analyzed.emit(True)

        fig_json = pio.to_json(fig)
        signal_data={
            'fig_json': fig_json,
            'transmissivity': T,
            'storativity': S,
            'start_time':TheisPage.start_time,
            'end_time':TheisPage.end_time
        }
        self.theis_signal_data.emit(signal_data)

    def create_report(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Theis Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
        if(file_path):
            TheisPage.pdf_obj.output(f'{file_path}')
            QMessageBox.information(self, 'Success', 'Report saved successfully!')