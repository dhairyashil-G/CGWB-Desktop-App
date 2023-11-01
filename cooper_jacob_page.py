from PyQt5 import uic
from PyQt5.QtWidgets import QScrollArea,QWidget, QFileDialog
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
import pandas as pd
import plotly.graph_objs as go
import sqlite3
import numpy as np
import math
from fpdf import FPDF
import os
from datetime import datetime
class CooperJacobPage(PageWindow,QObject):
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
        self.back_button.clicked.connect(self.goback)
        # self.calculate_cooper_jacob()
        self.plot_button.clicked.connect(self.calculate_cooper_jacob)
        self.download_report_button.clicked.connect(self.create_report)

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

    # def mse(self,actual, predicted):
    #     actual = np.array(actual)
    #     predicted = np.array(predicted)
    #     differences = np.subtract(actual, predicted)
    #     squared_differences = np.square(differences)
    #     return squared_differences.mean()
    
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
        self.storativity_value.setText("{:.3f}".format(S))
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
        title="Drawdown vs Time",
        xaxis_title="log Time (min)",
        yaxis_title="Drawdown (m)",
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
        # pdf.cell(0, 10, f'Root Mean Square Error = {round(mse_error, 3)}%', ln=1)
        pdf.ln(5)

        pdf.dashed_line(10, int(pdf.get_y()), 210 - 10,
                        int(pdf.get_y()), dash_length=1, space_length=1)
        CooperJacobPage.pdf_obj=pdf
    
    def create_report(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Cooper Jacob Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
        if(file_path):
            CooperJacobPage.pdf_obj.output(f'{file_path}')