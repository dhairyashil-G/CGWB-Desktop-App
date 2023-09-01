import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTableWidget, QTableWidgetItem, QWidget

class WellTablePage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Well Table Page')
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Create the table widget
        self.table_widget = QTableWidget(self)
        layout.addWidget(self.table_widget)

        # Set column count and headers
        self.table_widget.setColumnCount(4)  # Number of selected columns
        headers = ['Well Name', 'Location', 'Coordinates', 'Performed By']
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Load data from SQLite database
        self.load_data_from_database()

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
