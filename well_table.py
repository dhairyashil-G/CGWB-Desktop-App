import sqlite3
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QMessageBox, QLabel
from PyQt5 import uic, QtCore
from multiPageHandler import PageWindow
from PyQt5.QtCore import pyqtSignal, QObject


class WellTablePage(PageWindow, QObject):
    well_id_signal = pyqtSignal(int)

    def __init__(self):
        super(WellTablePage, self).__init__()
        uic.loadUi('well_table.ui', self)
        self.setWindowTitle('AquaProbe')
        self.setup_ui()

    def setup_ui(self):
        self.statusbar.showMessage("Version 1.0.0")
        self.setup_status_bar()
        self.setup_table_widget()
        self.setup_buttons()
        self.setup_menu_connections()

    def setup_status_bar(self):
        copyright_label = QLabel(
            "Copyright © 2024 AquaProbe. All rights reserved.")
        copyright_label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.statusbar.addPermanentWidget(copyright_label)

    def setup_table_widget(self):
        self.table_widget.setColumnWidth(1, 150)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 200)
        self.table_widget.setColumnWidth(4, 200)
        self.table_widget.setColumnWidth(5, 125)
        self.table_widget.setColumnWidth(6, 125)
        self.table_widget.setColumnWidth(7, 125)
        self.table_widget.setColumnWidth(8, 125)
        self.table_widget.setColumnHidden(0, True)

    def setup_buttons(self):
        self.back_button.clicked.connect(self.goback)
        self.create_well_button.clicked.connect(self.gocreatewell)

    def setup_menu_connections(self):
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

    def goback(self):
        self.goto('homepage')

    def gocreatewell(self):
        self.goto('createwell')

    def load_data_from_database(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            'SELECT "Id","WellName", "Location", "Coordinates", "PerformedBy" FROM WellData')
        selected_columns_data = cursor.fetchall()

        self.table_widget.setRowCount(len(selected_columns_data))
        for row_index, row_data in enumerate(selected_columns_data):
            for col_index, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value))
                self.table_widget.setItem(row_index, col_index, item)

            next_button = QPushButton("Analysis")
            read_button = QPushButton("Read")
            update_button = QPushButton("Update")
            delete_button = QPushButton("Delete")

            buttons = [next_button, read_button, update_button, delete_button]
            for idx, button in enumerate(buttons, 1):
                button.setProperty("row", row_index)
                button.clicked.connect(
                    lambda _, idx=idx: self.on_button_clicked(idx))

                self.table_widget.setCellWidget(
                    row_index, col_index + idx, button)

        conn.close()

    def on_button_clicked(self, button_idx):
        rownum = self.sender().property("row")
        id_item = self.table_widget.item(rownum, 0)
        row = id_item.text()

        if button_idx == 4:
            self.well_id_signal.emit(int(row))
            self.delete_row(row)
        elif button_idx == 3:
            self.well_id_signal.emit(int(row))
            self.goto('updatewell')
        elif button_idx == 2:
            self.well_id_signal.emit(int(row))
            self.goto('readwell')
        elif button_idx == 1:
            self.well_id_signal.emit(int(row))
            self.goto('preview')

    def delete_row(self, row):
        confirmation = QMessageBox.question(
            self, "Confirmation", "Are you sure you want to delete this well?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            try:
                cursor.execute('DELETE FROM WellData WHERE "Id" = ?', (row,))
                conn.commit()
                print(f"Deleted row with 'Id' {row} from the database.")
            except sqlite3.Error as e:
                print("SQLite error:", e)
                conn.rollback()
            finally:
                conn.close()

            self.table_widget.removeRow(int(row))
