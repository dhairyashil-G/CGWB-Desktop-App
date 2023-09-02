import sys
import sqlite3
from PyQt5.QtWidgets import QApplication,QTableWidgetItem
from PyQt5 import uic
from multiPageHandler import PageWindow

class WellTablePage(PageWindow):
    def __init__(self):
        super(WellTablePage,self).__init__()
        uic.loadUi('well_table.ui',self)
        self.table_widget.setColumnWidth(0,150)
        self.table_widget.setColumnWidth(1,150)
        self.table_widget.setColumnWidth(2,150)
        self.table_widget.setColumnWidth(3,150)

        self.back_button.clicked.connect(self.goback)

        # Load data from SQLite database
        self.load_data_from_database()

    def goback(self):
        self.goto('homepage')

    def load_data_from_database(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')  # Replace 'database.db' with your database file name
        cursor = conn.cursor()

        # Fetch selected columns from the WellData table
        cursor.execute('SELECT "WellName", "Location", "Coordinates", "PerformedBy" FROM WellData')
        selected_columns_data = cursor.fetchall()

        # Populate the table widget with the data
        self.table_widget.setRowCount(len(selected_columns_data))
        for row_index, row_data in enumerate(selected_columns_data):
            for col_index, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.table_widget.setItem(row_index, col_index, item)

        # Close the database connection
        conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    well_table_page = WellTablePage()
    well_table_page.show()
    sys.exit(app.exec_())
