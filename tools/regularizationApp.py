import sys
import reportParser
import numpy as np
from isotherm import Isotherm
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QLineEdit, QFileDialog, QLabel, QComboBox

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure


# noinspection PyAttributeOutsideInit
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWidgets()
        self.data = Isotherm()
        self.data.load_kernel()

        ##
        self.fitted_p = None
        self.fitted_restored = None
        self.fitted_real = None
        ##

    def initWidgets(self):
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QGridLayout(self._main)
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 10)))
        layout.addWidget(dynamic_canvas, 0, 0, 1, 2)
        layout.addWidget(NavigationToolbar(dynamic_canvas, self), 1, 0)

        dynamic_canvas_PSD = FigureCanvas(Figure(figsize=(5, 10)))
        layout.addWidget(dynamic_canvas_PSD, 2, 0, 1, 2)
        layout.addWidget(NavigationToolbar(dynamic_canvas_PSD, self), 3, 0)

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax_PSD = dynamic_canvas_PSD.figure.subplots()
        self._dynamic_ax_PSD.set_xscale('log')
        # colors.plot_colortable(mcolors.TABLEAU_COLORS, ncols=2, sort_colors=False)
        self.isothermLine, = self._dynamic_ax.plot([], [], marker=".", label="origin isotherm adsorption",
                                                   color="tab:blue")
        self.isothermLine_d, = self._dynamic_ax.plot([], [], marker=".", label="origin isotherm desorption",
                                                     color="tab:blue")
        self.fittedOriginLine, = self._dynamic_ax.plot([], [], marker=".", label="fitted origin", color="orange")
        # self.fittedOriginMeasuredLine, = self._dynamic_ax.plot([], [], marker="*", label="fitted measured")

        # self.interpolated_isothermLine, = self._dynamic_ax.plot([], [], marker=".", label="interpolated isotherm")
        self.restored_isothermLine, = self._dynamic_ax.plot([], [], marker=".", label="PSD isotherm",
                                                            color="tab:purple")
        self.definedPSDLine, = self._dynamic_ax_PSD.plot([], [], marker=".", label="defined PSD", color="tab:purple")
        self.referencePSDLine, = self._dynamic_ax_PSD.plot([], [], marker=".", label="reference PSD",
                                                           color="tab:orange")

        self._dynamic_ax.legend()
        self._dynamic_ax_PSD.legend()

        self.processButton = QtWidgets.QPushButton("Process")
        self.processButton.clicked.connect(self.process)
        self.alphaInput = QLineEdit()
        self.betaInput = QLineEdit()

        self.alphaInput.setText('0')
        self.betaInput.setText('0')

        layout.addWidget(QLabel("Alpha"), 4, 0)
        layout.addWidget(QLabel("Beta"), 4, 1)
        layout.addWidget(self.alphaInput, 5, 0)
        layout.addWidget(self.betaInput, 5, 1)
        layout.addWidget(self.processButton, 6, 0)

        openDialogBtn = QtWidgets.QPushButton(self)
        openDialogBtn.setText("Open file")
        layout.addWidget(openDialogBtn, 6, 1)
        openDialogBtn.clicked.connect(self.open_dialog)

        self.kernel_selection = QComboBox()
        self.kernel_selection.addItems(["../data/initial kernels/excel/Silica-loc-isoth1.xlsx",
                                        "../data/initial kernels/excel/Carbon-loc-isoth-N2.xlsx"])
        layout.addWidget(self.kernel_selection)
        self.kernel_selection.currentTextChanged.connect(self.kernel_changed)

        self.branch_selection = QComboBox()
        self.branch_selection.addItems(["adsorption", "desorption", "both"])
        layout.addWidget(self.branch_selection)
        self.branch_selection.currentTextChanged.connect(self.branch_changed)

        self.R_text = QLabel()
        layout.addWidget(self.R_text)

        self.R_file_text = QLabel()
        layout.addWidget(self.R_file_text)

    def process(self):
        if float(self.betaInput.text()) == 0: ######## tikhonov
            self.data.process_isotherm(float(self.alphaInput.text()), float(self.betaInput.text()),######
                                       branch=self.branch_selection.currentText(), regularization="tikhonov")########
        else:
            self.data.process_isotherm(float(self.alphaInput.text()), float(self.betaInput.text()),
                                       branch=self.branch_selection.currentText())

        self._dynamic_ax.set_ylim([0.95 * min(self.data.isothermData), 1.01 * max(self.data.isothermData)])
        self._dynamic_ax.set_xlim([0.99 * min(self.data.pressureData), 1.01 * max(self.data.pressureData)])
        self.isothermLine.set_data(self.data.pressureData, self.data.isothermData)
        self.isothermLine_d.set_data(self.data.pressureData_d, self.data.isothermData_d)

        # self.interpolated_isothermLine.set_data(self.data.interpolated_kernel_p, self.data.interpolated_isotherm)
        self.fittedOriginLine.set_data(self.fitted_p, self.fitted_restored)
        # self.fittedOriginMeasuredLine.set_data(self.fitted_p, self.fitted_real)

        self.isothermLine.figure.canvas.draw()
        self.isothermLine_d.figure.canvas.draw()
        # self.interpolated_isothermLine.figure.canvas.draw()
        # self.fittedOriginLine.figure.canvas.draw()
        self.fittedOriginLine.figure.canvas.draw()

        if self.branch_selection.currentText() == "adsorption":
            self.restored_isothermLine.set_data(self.data.interpolated_kernel_p, self.data.restored_isotherm)
        if self.branch_selection.currentText() == "desorption":
            self.restored_isothermLine.set_data(self.data.interpolated_kernel_p_d, self.data.restored_isotherm_d)
        if self.branch_selection.currentText() == "both":
            self.restored_isothermLine.set_data(
                np.concatenate((self.data.interpolated_kernel_p, self.data.interpolated_kernel_p_d[::-1])),
                np.concatenate((self.data.restored_isotherm, self.data.restored_isotherm_d[::-1])))

        self._dynamic_ax_PSD.set_ylim([0, 1.05 * max(self.data.defined_PSD * 0.000305501)])
        self._dynamic_ax_PSD.set_xlim([0.99 * min(self.data.kernel_a_array), 1.01 * max(self.data.kernel_a_array)])
        self.definedPSDLine.set_data(self.data.kernel_a_array, self.data.defined_PSD * 0.000305501)
        self.referencePSDLine.set_data(self.data.reference_pore_sizes,
                                       self.data.reference_PSD)
        self.definedPSDLine.figure.canvas.draw()
        self.restored_isothermLine.figure.canvas.draw()

        self.calculate_error()

    def calculate_error(self):
        defined_error = np.sum(np.abs(
            self.data.restored_isotherm - self.data.interpolated_isotherm) / self.data.interpolated_isotherm) / len(
            self.data.interpolated_isotherm)

        file_error = np.sum(np.abs(
            self.fitted_real - self.fitted_restored) / self.fitted_real) / len(
            self.fitted_real)
        self.R_text.setText(f"error: {round(defined_error * 100, 3)} %")
        self.R_file_text.setText(f"File error: {round(file_error * 100, 3)} %")

    def kernel_changed(self):
        self.data.load_kernel(self.kernel_selection.currentText())
        self.data.interpolate_isotherm()
        self.data.process_kernel()

    def branch_changed(self):
        pass

    # def calculate_errors(self):
    #     my_error = np.square(np.subtract(self.restored_isotherm, self.interpolated)).sum(axis=0) / len(self.restored_isotherm)
    #     quantachrome_error = np.square(np.subtract(self.fitted_restored, self.fitted_real)).sum(axis=0) / len(self.fitted_real)

    def open_dialog(self):
        fname = QFileDialog.getOpenFileName(self)
        try:
            raw_data = reportParser.get_isotherm_and_distribution(fname[0])
            data = reportParser.get_numpy_arrays(raw_data)
            self.data.isothermData = data["adsorption"]
            self.data.isothermData_d = data["desorption"]

            self.data.pressureData = data["p_adsorption"]
            self.data.pressureData_d = data["p_desorption"]

            self.data.reference_PSD = data["distribution"]
            self.data.reference_pore_sizes = data["pore_size"]

            self.fitted_p = data["fitted_p"]
            self.fitted_restored = data["fitted_restored"]
            self.fitted_real = data["fitted_real"]

            self.data.interpolate_isotherm()
            self.data.process_kernel()
            self.process()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
