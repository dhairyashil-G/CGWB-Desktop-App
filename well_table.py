import sqlite3
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import pyqtSignal, QObject

class WellTablePage(PageWindow,QObject):
    well_id_signal = pyqtSignal(int)
    
    def __init__(self):
        super(WellTablePage, self).__init__()
        uic.loadUi('well_table.ui', self)
        self.setWindowTitle('AquaProbe-Beta1')
        self.table_widget.setColumnWidth(0, 150)
        self.table_widget.setColumnWidth(1, 150)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setColumnHidden(0, True)

        self.back_button.clicked.connect(self.goback)
        self.table_widget.clicked.connect(self.singleclick)

        # Load data from SQLite database
        self.load_data_from_database()

    def goback(self):
        self.goto('homepage')

    def singleclick(self):
        for item in self.table_widget.selectedItems():
            print(item.row(), item.column(), item.text())

    def load_data_from_database(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')  # Replace 'database.db' with your database file name
        cursor = conn.cursor()

        # Fetch selected columns from the WellData table
        cursor.execute('SELECT "Id","WellName", "Location", "Coordinates", "PerformedBy" FROM WellData')
        selected_columns_data = cursor.fetchall()

        # Populate the table widget with the data
        self.table_widget.setRowCount(len(selected_columns_data))
        for row_index, row_data in enumerate(selected_columns_data):
            for col_index, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.table_widget.setItem(row_index, col_index, item)

            # Create "Delete" and "Next" buttons in the last two columns
            delete_button = QPushButton("Delete")
            next_button = QPushButton("Next")

            # Set button properties
            delete_button.setProperty("row", row_index)
            next_button.setProperty("row", row_index)

            # Connect button signals to functions
            delete_button.clicked.connect(self.delete_row)
            next_button.clicked.connect(self.next_row)

            # Add buttons to the table
            self.table_widget.setCellWidget(row_index, col_index + 1, delete_button)
            self.table_widget.setCellWidget(row_index, col_index + 2, next_button)

        # Close the database connection
        conn.close()

    def delete_row(self):
        # Get the row number from the button's property
        row = self.sender().property("row")
        
        # Retrieve the "Id" value from the table widget
        id_item = self.table_widget.item(row, 0)
        if id_item is not None:
            id_value = id_item.text()
        else:
            print("No 'Id' value found for row:", row)
            return

        # Connect to the SQLite database
        conn = sqlite3.connect('database.db')  # Replace 'database.db' with your database file name
        cursor = conn.cursor()

        try:
            # Use SQL DELETE statement to remove the row from the database
            cursor.execute('DELETE FROM WellData WHERE "Id" = ?', (id_value,))
            conn.commit()
            print(f"Deleted row with 'Id' {id_value} from the database.")
        except sqlite3.Error as e:
            print("SQLite error:", e)
            conn.rollback()
        finally:
            conn.close()

        # Remove the row from the table widget
        self.table_widget.removeRow(row)

    def next_row(self):
        # Get the row number from the button's property
        rownum = self.sender().property("row")
        id_item = self.table_widget.item(rownum, 0)
        row=id_item.text()
        self.well_id_signal.emit(int(row))
        # print("Next button clicked for row:", row)
        self.goto('preview')
