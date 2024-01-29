from PyQt5 import uic,QtWebEngineWidgets
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem,QHeaderView,QMessageBox,QApplication,QFileDialog
import sqlite3
import pandas as pd
from PyQt5.QtGui import QStandardItemModel
import plotly.graph_objs as go
import plotly.io as pio
import os

from fpdf import FPDF
from datetime import datetime

Qt = QtCore.Qt

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[section])
    
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.iloc[index.row()][index.column()]))
        return QtCore.QVariant()
    

class PreviewPage(PageWindow, QObject):
    def __init__(self):
        super(PreviewPage, self).__init__()
        uic.loadUi('preview.ui', self)
        self.setWindowTitle('AquaProbe-Beta1.1')
        self.back_button.clicked.connect(self.goback)
        self.theis_button.clicked.connect(self.gotheis)
        self.cooper_jacob_button.clicked.connect(self.gocooperjacob)
        self.theis_recovery_button.clicked.connect(self.gotheisrecovery)
        well_id_global=None
        self.plot_button.clicked.connect(self.show_plot)
        self.combined_report_button.clicked.connect(self.combined_report_save)

        PreviewPage.is_cooper_jacob_analyzed=False
        PreviewPage.cooper_jacob_data_dict=dict()
        PreviewPage.is_theis_analyzed=False
        PreviewPage.theis_data_dict=dict()
        PreviewPage.is_theis_recovery_analyzed=False
        PreviewPage.theis_recivery_data_dict=dict()

        # self.show_plot()
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

    def show_plot(self):
        self.loading_label.setText('Please wait...This might take some time...')
        QApplication.processEvents()

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
        csv_file_data = well_object.get('CsvFileData')
        dict_csv_data=eval(csv_file_data)
        df = pd.DataFrame(dict_csv_data)
        
        df_pumping_test = df[df['Time'] <= t_when_pumping_stopped]
        df_recovery_test = df[df['Time'] > t_when_pumping_stopped]

        print(df_pumping_test)
        # Rename columns in df_pumping_test
        df_recovery_test_new = df_recovery_test.copy()
        df_recovery_test_new.rename(columns={'Time': 'Time (min)', 'Drawdown': 'Drawdown (m)'}, inplace=True)

        # Rename columns in df_recovery_test
        df_pumping_test_new = df_pumping_test.copy()
        df_pumping_test_new.rename(columns={'Time': 'Time (min)', 'Drawdown': 'Drawdown (m)'}, inplace=True)

        model1 = PandasModel(df_pumping_test_new)
        self.pumping_table.setModel(model1)

        model2= PandasModel(df_recovery_test_new)
        self.recovery_table.setModel(model2)
        
    
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
        self.loading_label.setText('')


    def goback(self):
        self.goto('welltable') 
        PreviewPage.is_cooper_jacob_recovery_analyzed=False
        PreviewPage.is_theis_analyzed=False
        PreviewPage.is_theis_recovery_analyzed=False

    def gotheis(self):
        self.goto('theispage')

    def gocooperjacob(self):
        self.goto('cooperjacobpage')

    def gotheisrecovery(self):
        self.goto('theisrecoverypage')

    @pyqtSlot(int)
    def get_well(self, row):
        PreviewPage.well_id_global=row
        print('row received')
        
    @pyqtSlot(bool)
    def cooper_jacob_analyzed(self,value):
        PreviewPage.is_cooper_jacob_analyzed=True
        print(f'Cooper Jacob :{value}')

    @pyqtSlot(dict)
    def cooper_jacob_data(self,value):
        PreviewPage.cooper_jacob_data_dict=value

    @pyqtSlot(bool)
    def theis_analyzed(self,value):
        PreviewPage.is_theis_analyzed = value
        print(f'Theis :{value}')

    @pyqtSlot(dict)
    def theis_data(self,value):
        PreviewPage.theis_data_dict=value

    @pyqtSlot(bool)
    def theis_recovery_analyzed(self,value):
        PreviewPage.is_theis_recovery_analyzed = value
        print(f'Theis Recovery :{value}')

    @pyqtSlot(dict)
    def theis_recovery_data(self,value):
        PreviewPage.theis_recovery_data_dict=value


    def combined_report_save(self):
        print(PreviewPage.is_cooper_jacob_analyzed)
        if(PreviewPage.is_cooper_jacob_analyzed!=True):
            self.combined_report_button.setText('Save Combined Report')
            QMessageBox.warning(None,'Error','Please analyze Cooper-Jacob analysis first!')
        elif(PreviewPage.is_theis_analyzed!=True):
            self.combined_report_button.setText('Save Combined Report')
            QMessageBox.warning(None,'Error','Please analyze Theis analysis first!')
        elif(PreviewPage.is_theis_recovery_analyzed!=True):
            self.combined_report_button.setText('Save Combined Report')
            QMessageBox.warning(None,'Error','Please analyze Theis Recovery analysis first!')
        else:
            self.combined_report_button.setText('Please wait...')
            QApplication.processEvents()
            #pdf creation
            print(PreviewPage.cooper_jacob_data_dict)
            well_id = PreviewPage.well_id_global
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
            row = cursor.fetchone()

            well_object = {}
            if row:
                column_names = [desc[0] for desc in cursor.description]
                for i in range(len(column_names)):
                    well_object[column_names[i]] = row[i]


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
            pdf.cell(0, 10, 'Pumping Test Report', align='C', ln=1)
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
            lst2.append(f"Geology: {well_object.get('Geology')}")
            zones_list=eval(well_object.get('ZonesTappedIn'))
            lst1.append(f"Zones Tapped: {len(zones_list)}")
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
            
            zones_list=eval(well_object.get('ZonesTappedIn'))
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

            pdf.add_page()
            pdf.set_font('Arial', 'UB', 16)
            pdf.cell(0, 10, 'Cooper Jacob Test Report', align='C', ln=1)
            pdf.ln(5)

            pdf.set_font('Arial',"", 12)
            pdf.cell(0,10,"Test Parameters:",ln=1)
            lst3=list()
            lst4=list()
            lst3.append(f"Analysis Start Time: {PreviewPage.cooper_jacob_data_dict.get('start_time')} min")
            lst4.append(f"Analysis End Time: {PreviewPage.cooper_jacob_data_dict.get('end_time')} min")
            lst3.append(f"x-intercept value : {round(PreviewPage.cooper_jacob_data_dict.get('x_intercept'),3)}")
            lst4.append(f"Slope value : {round(PreviewPage.cooper_jacob_data_dict.get('slope'),3)}")
            for item1, item2 in zip(lst3, lst4):
                pdf.cell(col_width, 10, item1, border=1)
                pdf.cell(col_width, 10, item2, border=1)
                pdf.ln(10)
            pdf.ln(5)

            pdf.set_font('Arial', 'B', 13)
            pdf.cell(0, 10, "Graphical Interpretation", ln=1)
            reconstructed_fig = pio.from_json(PreviewPage.cooper_jacob_data_dict.get('fig_json'))
            reconstructed_fig.write_image("fig1.png")
            pdf.image('fig1.png', w=200, h=150)
            os.remove("fig1.png")
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Transmissivity : {round(PreviewPage.cooper_jacob_data_dict.get('transmissivity'), 3)} m²/day", ln=1)
            pdf.cell(0, 10, f"""Storativity : {"{:.8f}".format(PreviewPage.cooper_jacob_data_dict.get('storativity'))}""", ln=1)
            # pdf.cell(0, 10, f'Root Mean Square Error = {round(mse_error, 3)}%', ln=1)
            pdf.ln(5)


            pdf.add_page()
            pdf.set_font('Arial', 'UB', 16)
            pdf.cell(0, 10, 'Theis Test Report', align='C', ln=1)
            pdf.ln(5)

            pdf.set_font('Arial',"", 12)
            pdf.cell(0,10,"Test Parameters:",ln=1)
            lst3=list()
            lst4=list()
            lst3.append(f"Analysis Start Time: {PreviewPage.theis_data_dict.get('start_time')} min")
            lst4.append(f"Analysis End Time: {PreviewPage.theis_data_dict.get('end_time')} min")
            for item1, item2 in zip(lst3, lst4):
                pdf.cell(col_width, 10, item1, border=1)
                pdf.cell(col_width, 10, item2, border=1)
                pdf.ln(10)
            pdf.ln(5)

            pdf.set_font('Arial', 'B', 13)
            pdf.cell(0, 10, "Graphical Interpretation", ln=1)
            reconstructed_fig = pio.from_json(PreviewPage.theis_data_dict.get('fig_json'))
            reconstructed_fig.write_image("fig2.png")
            pdf.image('fig2.png', w=200, h=150)
            os.remove("fig2.png")
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Transmissivity : {round(PreviewPage.theis_data_dict.get('transmissivity'), 3)} m²/day", ln=1)
            pdf.cell(0, 10, f"""Storativity : {"{:.8f}".format(PreviewPage.theis_data_dict.get('storativity'))}""", ln=1)
            # pdf.cell(0, 10, f'Root Mean Square Error = {round(mse_error, 3)}%', ln=1)
            pdf.ln(5)

            pdf.add_page()
            pdf.set_font('Arial', 'UB', 16)
            pdf.cell(0, 10, 'Theis Recovery Test Report', align='C', ln=1)
            pdf.ln(5)

            pdf.set_font('Arial',"", 12)
            pdf.cell(0,10,"Test Parameters:",ln=1)
            lst3=list()
            lst4=list()
            lst3.append(f"Analysis Start Time: {PreviewPage.theis_recovery_data_dict.get('start_time')} min")
            lst4.append(f"Analysis End Time: {PreviewPage.theis_recovery_data_dict.get('end_time')} min")
            lst3.append(f"x-intercept value : {round(PreviewPage.theis_recovery_data_dict.get('x_intercept'),3)}")
            lst4.append(f"Slope value : {round(PreviewPage.theis_recovery_data_dict.get('slope'),3)}")
            for item1, item2 in zip(lst3, lst4):
                pdf.cell(col_width, 10, item1, border=1)
                pdf.cell(col_width, 10, item2, border=1)
                pdf.ln(10)
            pdf.ln(5)

            pdf.set_font('Arial', 'B', 13)
            pdf.cell(0, 10, "Graphical Interpretation", ln=1)
            reconstructed_fig = pio.from_json(PreviewPage.theis_recovery_data_dict.get('fig_json'))
            reconstructed_fig.write_image("fig3.png")
            pdf.image('fig3.png', w=200, h=150)
            os.remove("fig3.png")
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Transmissivity : {round(PreviewPage.theis_recovery_data_dict.get('transmissivity'), 3)} m²/day", ln=1)
            pdf.cell(0, 10, f"""Delta S : {"{:.3f}".format(PreviewPage.theis_recovery_data_dict.get('deltas'))}""", ln=1)
            # pdf.cell(0, 10, f'Root Mean Square Error = {round(mse_error, 3)}%', ln=1)
            pdf.ln(5)


            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime('%d-%m-%y,%H-%M-%S')
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Combined Report {formatted_datetime}", "PDF Files (*.pdf)", options=options)
            if(file_path):
                pdf.output(f'{file_path}')
                QMessageBox.information(self, 'Success', 'Report saved successfully!')
                self.combined_report_button.setText('Save Combined Report')
            else:
                self.combined_report_button.setText('Save Combined Report')