from PyQt5 import uic,QtWebEngineWidgets
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem,QHeaderView,QMessageBox,QApplication
import sqlite3
import pandas as pd
from PyQt5.QtGui import QStandardItemModel
import plotly.graph_objs as go

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
        csv_file_url = well_object.get('CsvFilePath', '')
        print(csv_file_url)
        try:
            df = pd.read_csv(csv_file_url)
        except Exception as e:
            print(e)
            
            QMessageBox.critical(None,"Error","File not found at given location!")
            self.loading_label.setText('')
            self.goto('welltable')

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
        
