import sys
import sqlite3
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button = QtWidgets.QPushButton('Plot', self)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.browser)

        self.button.clicked.connect(self.show_graph)
        self.resize(1000, 800)

    def show_graph(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Define the well_id you want to fetch (replace with your desired well_id)
        well_id = 4  # Replace with the desired well_id

        # Fetch selected columns for the well with the specified Id
        cursor.execute('SELECT * FROM WellData WHERE "Id" = ?', (well_id,))
        row = cursor.fetchone()

        # Initialize an empty dictionary to store the data
        well_object = {}

        if row:
            # Extract the column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Populate the dictionary with column names as keys and corresponding values
            for i in range(len(column_names)):
                well_object[column_names[i]] = row[i]

        # Fetch data from the well_object
        t_when_pumping_stopped = well_object.get('TimeWhenPumpingStopped', 0)
        csv_file_url = well_object.get('CsvFilePath', '')

        # Fetch data from the CSV file
        df = pd.read_csv(csv_file_url)
        df_pumping_test = df[df['Time'] <= t_when_pumping_stopped]
        df_recovery_test = df[df['Time'] > t_when_pumping_stopped]

        # Create the Plotly graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_pumping_test['Time'], y=df_pumping_test['Drawdown'],
                                 mode='lines+markers',
                                 name='Pumping Data'))
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
        # Convert the Plotly graph to HTML
        graph_html = pio.to_html(fig, full_html=False)

        # Display the graph HTML content in the QWebEngineView widget
        self.browser.setHtml(graph_html)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
