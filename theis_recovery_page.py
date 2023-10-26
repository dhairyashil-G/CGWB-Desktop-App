from PyQt5 import uic
from multiPageHandler import PageWindow
from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5.QtWidgets import QFileDialog
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from scipy.special import exp1
import pandas as pd
import numpy as np
from fpdf import FPDF
import os
from datetime import datetime

class TheisRecoveryPage(PageWindow,QObject):
    def __init__(self):
        super(TheisRecoveryPage, self).__init__()
        TheisRecoveryPage.well_id_global=None
        TheisRecoveryPage.pdf_obj=None
        uic.loadUi('theis_recovery.ui', self)
        # self.update_button.clicked.connect(self.calculate_theis)
        self.back_button.clicked.connect(self.goback)
        # self.download_report_button.clicked.connect(self.create_report)

    @pyqtSlot(int)
    def get_well(self, row):
        TheisRecoveryPage.well_id_global=row

    def goback(self):
        self.goto('preview')
