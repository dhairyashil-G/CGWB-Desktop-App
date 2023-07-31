import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class HomePage(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the main window properties
        self.setWindowTitle('Pumping Test Data Analysis')

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap('path_to_logo_image.png')  # Replace 'path_to_logo_image.png' with the actual logo image file path
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label)
        header_layout.addWidget(QLabel('Pumping Test Data Analysis'))
        layout.addLayout(header_layout)

        # Description
        description_label = QLabel(
            "Welcome to the Pumping Test Data Analysis application. "
            "This application allows you to analyze pumping test data and extract useful insights."
        )
        description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)

        # Buttons for analysis options
        analysis_layout = QHBoxLayout()
        analysis_layout.addWidget(QPushButton("Data Visualization"))
        analysis_layout.addWidget(QPushButton("Hydraulic Parameters"))
        # Add more buttons for other analysis options as needed
        layout.addLayout(analysis_layout)
