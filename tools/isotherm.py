import numpy as np
import inverse
import pandas as pd


def load_kernel_branch(kernel_path, branch, kernel_p_array, kernel_a_array, kernel_array_of_isotherms):
    list_name = kernel_path
    dataframe = pd.read_excel(list_name, header=None, sheet_name=branch)
    P_START = 0  # индекс min давления
    P_END = -33  # индекс max давления
    kernel_p_array = np.array(dataframe[0][P_START:P_END])  # сетка давлений
    kernel_a_array = np.array(dataframe.iloc[0][1:])  # сетка размеров пор
    kernel_array_of_isotherms = np.empty(
        (len(kernel_a_array), len(kernel_p_array)))  # массив изотерм с i-м размером пор
    for i in range(len(kernel_a_array)):  # заполняем массив изотерм из таблицы pandas
        kernel_array_of_isotherms[i] = dataframe[i + 1][P_START:P_END]
    return kernel_p_array, kernel_a_array, kernel_array_of_isotherms


def interpolate_isotherm_branch(kernel_p_array, max_p_idx, min_p_idx, interpolated_kernel_p, interpolated_isotherm,
                                pressureData, isothermData):
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    kernel_p_array = kernel_p_array[~np.isnan(kernel_p_array)]
    kernel_p_array = kernel_p_array[~np.isnan(kernel_p_array)]
    interpolated_isotherm_raw = np.interp(kernel_p_array, pressureData, isothermData)
    max_p = np.max(pressureData)
    min_p = np.min(pressureData)
    max_p_idx = find_nearest(kernel_p_array, max_p)
    min_p_idx = find_nearest(kernel_p_array, min_p)
    interpolated_kernel_p = kernel_p_array[min_p_idx:max_p_idx]
    interpolated_isotherm = interpolated_isotherm_raw[min_p_idx:max_p_idx]
    return kernel_p_array, max_p_idx, min_p_idx, interpolated_kernel_p, interpolated_isotherm, pressureData, isothermData


class Isotherm():
    def __init__(self):
        self.name = "New isotherm"
        self.isothermData = None
        self.pressureData = None
        self.isothermData_d = None
        self.pressureData_d = None
        self.interpolated_kernel_p = None
        self.interpolated_isotherm = None
        self.interpolated_kernel_p_d = None
        self.interpolated_isotherm_d = None
        self.restored_isotherm = None
        self.restored_isotherm_d = None
        self.defined_PSD = None
        self.defined_PSD_d = None
        self.reference_PSD = None
        self.reference_pore_sizes = None

        self.kernel_p_array = None
        self.kernel_p_array_d = None
        self.kernel_a_array = None
        self.kernel_a_array_d = None
        self.kernel_array_of_isotherms = None
        self.kernel_array_of_isotherms_d = None
        self.interpolated_kernel_isotherms = None
        self.interpolated_kernel_isotherms_d = None

        self.max_p_idx = None
        self.min_p_idx = None
        self.max_p_idx_d = None
        self.min_p_idx_d = None

    def load_kernel(self, kernel_path="../data/initial kernels/excel/Silica-loc-isoth1.xlsx"):
        self.kernel_p_array, self.kernel_a_array, self.kernel_array_of_isotherms = load_kernel_branch(kernel_path,
                                                                                                      "Adsorption",
                                                                                                      self.kernel_p_array,
                                                                                                      self.kernel_a_array,
                                                                                                      self.kernel_array_of_isotherms)
        self.kernel_p_array_d, self.kernel_a_array_d, self.kernel_array_of_isotherms_d = load_kernel_branch(kernel_path,
                                                                                                            "Desorption",
                                                                                                            self.kernel_p_array_d,
                                                                                                            self.kernel_a_array_d,
                                                                                                            self.kernel_array_of_isotherms_d)

    def interpolate_isotherm(self):
        self.kernel_p_array, self.max_p_idx, self.min_p_idx, self.interpolated_kernel_p, self.interpolated_isotherm, self.pressureData, self.isothermData = interpolate_isotherm_branch(
            self.kernel_p_array, self.max_p_idx, self.min_p_idx,
            self.interpolated_kernel_p, self.interpolated_isotherm, self.pressureData,
            self.isothermData)

        if self.isothermData_d is not None:
            self.kernel_p_array_d, self.max_p_idx_d, self.min_p_idx_d, self.interpolated_kernel_p_d, self.interpolated_isotherm_d, self.pressureData_d, self.isothermData_d = interpolate_isotherm_branch(
                self.kernel_p_array_d, self.max_p_idx_d, self.min_p_idx_d,
                self.interpolated_kernel_p_d, self.interpolated_isotherm_d, self.pressureData_d,
                self.isothermData_d)

    def process_isotherm(self, alpha, beta, branch="adsorption", regularization="default"):
        if regularization == "default":
            if branch == "adsorption":
                minimizationResult = inverse.fit_SLSQP(self.interpolated_isotherm, self.interpolated_kernel_isotherms,
                                                       alpha=alpha,
                                                       beta=beta,
                                                       a_array=self.kernel_a_array)
            elif branch == "desorption":
                minimizationResult = inverse.fit_SLSQP(self.interpolated_isotherm_d, self.interpolated_kernel_isotherms_d,
                                                       alpha=alpha,
                                                       beta=beta,
                                                       a_array=self.kernel_a_array_d)
            elif branch == "both":
                minimizationResult = inverse.fit_SLSQP_both_branches(self.interpolated_isotherm,
                                                                     self.interpolated_isotherm_d,
                                                                     self.interpolated_kernel_isotherms,
                                                                     self.interpolated_kernel_isotherms_d,
                                                                     beta=beta,
                                                                     a_array=self.kernel_a_array)
            else:
                return
        elif regularization == "tikhonov":
            minimizationResult = inverse.fit_linear(self.interpolated_isotherm, self.interpolated_kernel_isotherms, alpha)
        self.defined_PSD = minimizationResult.x
        self.restored_isotherm = np.dot(self.interpolated_kernel_isotherms.T, self.defined_PSD)
        self.restored_isotherm_d = np.dot(self.interpolated_kernel_isotherms_d.T, self.defined_PSD)

    def process_kernel(self):
        interpolated_kernel_isotherms = []
        for i in range(len(self.kernel_array_of_isotherms)):
            interpolated_kernel_isotherms.append(self.kernel_array_of_isotherms[i][self.min_p_idx:self.max_p_idx])
        self.interpolated_kernel_isotherms = np.array(interpolated_kernel_isotherms)

        interpolated_kernel_isotherms_d = []
        for i in range(len(self.kernel_array_of_isotherms_d)):
            interpolated_kernel_isotherms_d.append(
                self.kernel_array_of_isotherms_d[i][self.min_p_idx_d:self.max_p_idx_d])
        self.interpolated_kernel_isotherms_d = np.array(interpolated_kernel_isotherms_d)
