from PyQt5 import uic
from PyQt5.QtWidgets import QScrollArea,QWidget, QFileDialog,QMessageBox,QApplication
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot,pyqtSignal
from PyQt5.QtGui import QMovie
import pandas as pd
import plotly.graph_objs as go
import sqlite3
import plotly.io as pio
import numpy as np
import math
from fpdf import FPDF
import os
from datetime import datetime
class CooperJacobPage(PageWindow,QObject):
    cooper_jacob_analyzed=pyqtSignal(bool)
    cooper_jacob_signal_data=pyqtSignal(dict)

    def __init__(self):
        super(CooperJacobPage, self).__init__()
         # Create a scroll area to contain the entire window's content
        # self.scroll_area = QScrollArea(self)
        # self.scroll_area.setWidgetResizable(True)

        # # Create a widget to hold all the window's content
        # self.scroll_widget = QWidget()
        # self.scroll_area.setWidget(self.scroll_widget)

        # # Set the scroll area as the central widget of the main window
        # self.setCentralWidget(self.scroll_area)
        uic.loadUi('cooper_jacob.ui', self)
        self.setWindowTitle('AquaProbe-Beta1.1')
        CooperJacobPage.well_id_global=None
        CooperJacobPage.pdf_obj=None
        CooperJacobPage.slope=0
        CooperJacobPage.x_intercept=0
        CooperJacobPage.start_time = 0
        CooperJacobPage.end_time = 0
        self.back_button.clicked.connect(self.goback)
        # self.calculate_cooper_jacob()
        
        # self.loading_label.hide()

        self.adjust_x_intercept.valueChanged.connect(self.x_intercept_changed)
        self.adjust_slope.valueChanged.connect(self.slope_changed)

        self.adjust_start_time.valueChanged.connect(self.start_time_changed)
        self.adjust_end_time.valueChanged.connect(self.end_time_changed)
        
        self.plot_button.clicked.connect(self.calculate_cooper_jacob)
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

    @pyqtSlot(float)
    def x_intercept_changed(self,value):
        CooperJacobPage.x_intercept=value

    @pyqtSlot(float)
    def slope_changed(self,value):
        CooperJacobPage.slope=value
    
    @pyqtSlot(float)
    def start_time_changed(self,value):
        CooperJacobPage.start_time=value
        self.adjust_x_intercept.setValue(0)
        self.adjust_slope.setValue(0)
    
    @pyqtSlot(float)
    def end_time_changed(self,value):
        CooperJacobPage.end_time=value
        self.adjust_x_intercept.setValue(0)
        self.adjust_slope.setValue(0)

    @pyqtSlot(int)
    def get_well(self, row):
        CooperJacobPage.well_id_global=row

    def goback(self):
        self.goto('preview')
    
    def output_info_table(pdf, df):
        table_cell_width = 90
        table_cell_height = 12
        pdf.set_font('Arial', '', 12)
        cols = df.columns
        for row in df.itertuples():
            for col in cols:
                value = str(getattr(row, col))
                table_cell_width = 90
                pdf.cell(table_cell_width, table_cell_height,
                        value, align='L', border=1)
            pdf.ln(table_cell_height)
    
    def calculate_drawdown(self,Q, T, t, S, r):
        return ((2.303*Q)/(4*math.pi*T))*(math.log10((2.25*T*t)/(S*r*r)))

    def calculate_u(self,r, S, T, t):
        return (r*r*S)/(4*T*t)

    def mse(self,actual, predicted):
        actual = np.array(actual)
        predicted = np.array(predicted)
        differences = np.subtract(actual, predicted)
        squared_differences = np.square(differences)
        return squared_differences.mean()
    
    def calculate_cooper_jacob(self):
        self.loading_label.setText('Please wait...This might take some time...')
        # self.movie = QMovie("loading_gif.gif")
        # self.loading_label.setMovie(self.movie)
        # self.loading_label.show()
        # self.movie.start()
        QApplication.processEvents()
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
        csv_file_data = well_object.get('CsvFileData')
        dict_csv_data=eval(csv_file_data)
        df = pd.DataFrame(dict_csv_data)
        if(self.adjust_start_time.value()==0 and self.adjust_end_time.value()==0):
            start_time = df['Time'].iloc[0]
            end_time = t_when_pumping_stopped
            self.adjust_start_time.setValue(start_time)
            self.adjust_end_time.setValue(end_time)
            CooperJacobPage.start_time=start_time
            CooperJacobPage.end_time=end_time

        df = df.loc[(CooperJacobPage.start_time <= df['Time']) & (df['Time'] <= CooperJacobPage.end_time)]

        x_data = np.array(df['Time'])
        y_data = np.array(df['Drawdown'])

        if(self.adjust_slope.value()==0 and self.adjust_x_intercept.value()==0):
            print('if block')
            slope, y_intercept = np.polyfit(np.log(x_data), y_data, 1)
            x_intercept = np.exp((-y_intercept)/slope)
            x_intercept = np.log(x_intercept)  #log of x-intercept
            self.adjust_slope.setValue(round(slope,6))
            self.adjust_x_intercept.setValue(round(np.exp(x_intercept),6))
            # self.adjust_x_intercept.setValue(round(x_intercept,6))
            CooperJacobPage.x_intercept=round(np.exp(x_intercept),6)
            # CooperJacobPage.x_intercept=round(x_intercept,6)
            CooperJacobPage.slope=round(slope,6)
        

        x_intercept=np.log(CooperJacobPage.x_intercept)
        # x_intercept=CooperJacobPage.x_intercept
        slope=CooperJacobPage.slope

        y_intercept = ((-slope)*(x_intercept))
        # y_intercept = ((-slope)*(np.log(x_intercept)))


        delta_s = abs((slope*math.log(100) + y_intercept) -
                    (slope*math.log(10) + y_intercept))
        t_0 = np.exp((-y_intercept)/slope)

        T = (2.303*Q)/(4*math.pi*delta_s)
        S = (2.25*T*(t_0/1440)) / (r*r)
        
        
        calculate_drawdown_list = list()
        u_list = list()
        error_list = list()
        for index, row in df.iterrows():
            drawdown = row['Drawdown']
            time = row['Time']/1440
            calculated_drawdown = self.calculate_drawdown(Q, T, time, S, r)
            calculate_drawdown_list.append(calculated_drawdown)
            u = self.calculate_u(r, S, T, time)
            u_list.append(u)
            error = (drawdown-calculated_drawdown)/drawdown
            error_list.append(error)

        df_calc = df
        df_calc['Calculated_Drawdown'] = calculate_drawdown_list
        df_calc['u'] = u_list
        df_calc['Error'] = error_list
        df_calc = df_calc.round(decimals=3)

        mse_error = self.mse(df['Drawdown'], df['Calculated_Drawdown'])

        self.transmissivity_value.setText(str(round(T,3)))
        self.storativity_value.setText("{:.8f}".format(S))
        # self.rms_error_value.setText(str(round(mse_error,3)))

    # def show_plot(self,x_data,y_data,y_intercept,slope):
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
        title="Method: Cooper Jacob",
        xaxis_title="log Time (min)",
        yaxis_title="Drawdown (m)",
        legend_title="Legend",
        title_x=0.5
        )

        fig.update_layout(
            annotations=[
                dict(
                    text="Drawdown vs Time",
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
        pdf.cell(0, 10, 'Cooper Jacob Test Report', align='C', ln=1)
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
        lst1.append(f"Analysis Start Time: {CooperJacobPage.start_time} min")
        lst2.append(f"Analysis End Time: {CooperJacobPage.end_time} min")
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
        lst3.append(f"Analysis Start Time: {CooperJacobPage.start_time} min")
        lst4.append(f"Analysis End Time: {CooperJacobPage.end_time} min")
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
        pdf.cell(0, 10, f'Storativity : {"{:.8f}".format(S)}', ln=1)
        # pdf.cell(0, 10, f'Root Mean Square Error = {round(mse_error, 3)}%', ln=1)
        pdf.ln(5)

        CooperJacobPage.pdf_obj=pdf

        # self.movie.stop()
        # self.loading_label.clear()
        self.loading_label.setText('')
        self.cooper_jacob_analyzed.emit(True)

        fig_json = pio.to_json(fig)
        signal_data={
            'fig_json': fig_json,
            'slope': slope,
            'x_intercept': np.exp(x_intercept),
            'y_intercept': y_intercept,
            'transmissivity': T,
            'storativity': S,
            'start_time':CooperJacobPage.start_time,
            'end_time':CooperJacobPage.end_time
        }
        self.cooper_jacob_signal_data.emit(signal_data)
        
    def create_report(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Cooper Jacob Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
        if(file_path):
            CooperJacobPage.pdf_obj.output(f'{file_path}')
            QMessageBox.information(self, 'Success', 'Report saved successfully!')