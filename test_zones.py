import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem

class NumberListApp(QWidget):
    def __init__(self):
        super(NumberListApp, self).__init__()

        self.number_list = []  # List to store lists representing ranges

        # Input fields for the range
        self.start_input = QLineEdit(self)
        self.start_input.setPlaceholderText("Start value")
        self.end_input = QLineEdit(self)
        self.end_input.setPlaceholderText("End value")

        # Add button
        self.add_button = QPushButton("Add Range", self)
        self.add_button.clicked.connect(self.addRange)

        # Table to display ranges
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)  # Two columns for start and end values

        # Set headers for the columns
        self.table.setHorizontalHeaderLabels(["Start", "End"])

        # Layout
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_input)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.setWindowTitle("Number Range List App")
        self.setGeometry(100, 100, 400, 300)

    def addRange(self):
        try:
            start_value = int(self.start_input.text())
            end_value = int(self.end_input.text())
            self.number_list.append([start_value, end_value])
            self.updateTable()
            self.start_input.clear()
            self.end_input.clear()
            print(self.number_list)
        except ValueError:
            pass  # Ignore if the input is not a valid number

    def updateTable(self):
        num_ranges = len(self.number_list)

        self.table.setRowCount(num_ranges)

        for i, (start, end) in enumerate(self.number_list):
            self.table.setItem(i, 0, QTableWidgetItem(str(start)))
            self.table.setItem(i, 1, QTableWidgetItem(str(end)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NumberListApp()
    ex.show()
    sys.exit(app.exec_())
