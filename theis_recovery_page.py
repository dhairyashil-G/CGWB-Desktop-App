from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot,pyqtSignal
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QApplication
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
import plotly.io as pio

class TheisRecoveryPage(PageWindow,QObject):
    theis_recovery_analyzed=pyqtSignal(bool)
    theis_recovery_signal_data=pyqtSignal(dict)
    def __init__(self):
        super(TheisRecoveryPage, self).__init__()
        TheisRecoveryPage.well_id_global=None
        TheisRecoveryPage.pdf_obj=None
        TheisRecoveryPage.start_time = 0
        TheisRecoveryPage.end_time = 0
        uic.loadUi('theis_recovery.ui', self)
        self.setWindowTitle('AquaProbe-Beta1.1')
        self.plot_button.clicked.connect(self.calculate_theis_recovery)
        self.back_button.clicked.connect(self.goback)
        self.adjust_start_time.valueChanged.connect(self.start_time_changed)
        self.adjust_end_time.valueChanged.connect(self.end_time_changed)
        self.download_report_button.clicked.connect(self.create_report)
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
        TheisRecoveryPage.well_id_global=row

    @pyqtSlot(float)
    def start_time_changed(self,value):
        TheisRecoveryPage.start_time=value
        self.adjust_x_intercept.setValue(0)
        self.adjust_slope.setValue(0)
    
    @pyqtSlot(float)
    def end_time_changed(self,value):
        TheisRecoveryPage.end_time=value
        self.adjust_x_intercept.setValue(0)
        self.adjust_slope.setValue(0)

    def goback(self):
        self.goto('preview')

    def calculate_theis_recovery(self):
        self.loading_label.setText('Please wait...This might take some time...')
        QApplication.processEvents()
        well_id = TheisRecoveryPage.well_id_global 

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
        df = pd.DataFrame(dict_csv_data)
        df_org = pd.DataFrame(dict_csv_data)

        df = df.loc[df['Time'] > t_when_pumping_stopped]
        if(self.adjust_start_time.value()==0 and self.adjust_end_time.value()==0):
            start_time = t_when_pumping_stopped
            end_time = df['Time'].iloc[-1]
            self.adjust_start_time.setValue(start_time)
            self.adjust_end_time.setValue(end_time)
            TheisRecoveryPage.start_time=start_time
            TheisRecoveryPage.end_time=end_time

        df = df.loc[(TheisRecoveryPage.start_time <= df['Time']) & (df['Time'] <= TheisRecoveryPage.end_time)]

        df['Time'] = df['Time']-t_when_pumping_stopped
        df.rename(columns={'Time': 't_dash',
                'Drawdown': 'Residual_Drawdown'}, inplace=True)
        df['t'] = df['t_dash']+t_when_pumping_stopped
        df['t_by_t_dash'] = df['t']/df['t_dash']
        df = df[['t', 't_dash', 't_by_t_dash', 'Residual_Drawdown']]

        df_org = df_org.loc[(df_org['Time'] > t_when_pumping_stopped_org)]
        df_org['Time'] = df_org['Time']-t_when_pumping_stopped_org
        df_org.rename(columns={'Time': 't_dash',
                'Drawdown': 'Residual_Drawdown'}, inplace=True)
        df_org['t'] = df_org['t_dash']+t_when_pumping_stopped_org
        df_org['t_by_t_dash'] = df_org['t']/df_org['t_dash']
        df_org = df_org[['t', 't_dash', 't_by_t_dash', 'Residual_Drawdown']]
        x_org_data = np.array(df_org['t_by_t_dash'])
        y_org_data = np.array(df_org['Residual_Drawdown'])

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
        
        # To add this create a label in ui with name "realtive_change_s_value" and uncomment in pdf creation code
        # self.relative_change_s_value.setText(str(round(ratio_of_S,3)))

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=x_org_data, y=y_org_data,
                                mode='lines+markers',
                                name='Actual Data'))
        fig.update_xaxes(type="log")

        fig.add_trace(go.Scatter(x=x_data, y=y_data,
                                mode='lines+markers',
                                name='Selected Data'))
        fig.update_xaxes(type="log")

        fig.add_trace(go.Scatter(x=np.exp((y_data - y_intercept)/slope), y=y_data,
                                mode='lines+markers',
                                name='Fitting Line'))
        fig.update_xaxes(type="log")

        fig.update_layout(
            title="Method: Theis Recovery",
            xaxis_title="log t/t'",
            yaxis_title="Residual Drawdown (m)",
            legend_title="Legend",
            title_x=0.5,
            xaxis=dict(rangeslider=dict(visible=True))
        )
        fig.update_layout(
            annotations=[
                dict(
                    text="Residual Drawdown Vs t/t'",
                    x=0.54,
                    y=1.1,  # Adjust the y-coordinate to position the text below the graph
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    font=dict(size=14),
                )
            ]
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
        pdf.cell(0, 10, 'Theis Recovery Test Report', align='C', ln=1)
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
        lst3.append(f"Analysis Start Time: {TheisRecoveryPage.start_time} min")
        lst4.append(f"Analysis End Time: {TheisRecoveryPage.end_time} min")
        lst3.append(f"x-intercept value: {round(x_intercept,3)}")
        lst4.append(f"Slope value: {round(slope,3)}")
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
        pdf.cell(0, 10, f'delta S : {round(delta_s_dash,3)}', ln=1)
        # pdf.cell(0, 10, f'Relative Change in S : {round(ratio_of_S, 3)}%', ln=1)
        pdf.ln(5)

        TheisRecoveryPage.pdf_obj=pdf
        self.loading_label.setText('')
        self.theis_recovery_analyzed.emit(True)

        fig_json = pio.to_json(fig)
        signal_data={
            'fig_json': fig_json,
            'slope': slope,
            'x_intercept': x_intercept,
            'y_intercept': y_intercept,
            'transmissivity': T,
            'deltas': delta_s_dash,
            'start_time':TheisRecoveryPage.start_time,
            'end_time':TheisRecoveryPage.end_time
        }
        self.theis_recovery_signal_data.emit(signal_data)

    def create_report(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Theis Recovery Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
        print(file_path)
        if(file_path):
            TheisRecoveryPage.pdf_obj.output(f'{file_path}')
            QMessageBox.information(self, 'Success', 'Report saved successfully!')