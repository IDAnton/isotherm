import os
import re

import numpy as np
import pandas as pd
from fontTools.misc.cython import returns

from inverse import fit_linear


pressures = np.load("../data/initial kernels/Pressure_Silica.npy")
def filer_pressure_range(isotherm):
    if isotherm['p/p0'][0] >= 0.01 and isotherm['p/p0'][len(isotherm['p/p0'])-1] < pressures[-10]:
        return False
    return True

def filter_number_of_points(isotherm, min_number_of_points=15):
    if len(isotherm["p/p0"]) <= min_number_of_points:
        return False
    return True

def filter_pressure_fall(isotherm):
    for i in range(len(isotherm["p/p0"])-1):
        if isotherm["p/p0"][i] >= isotherm["p/p0"][i+1]:
            return False
    return True

def filter_adsorption_fall(isotherm):
    for i in range(len(isotherm["p/p0"])-1):
        if isotherm["Quantity Adsorbed (mmol/g)"][i+1]/isotherm["Quantity Adsorbed (mmol/g)"][i] < 1:
            return False
    return True


def filter_isotherms(dataframes):
    new_dataframes = []
    filters = [filter_number_of_points, filter_pressure_fall, filter_adsorption_fall, filer_pressure_range]
    for dataframe in dataframes:
        is_bad_isotherm = False
        for f in filters:
            if not f(dataframe[0]):
                is_bad_isotherm = True
                break
        if not is_bad_isotherm:
            new_dataframes.append(dataframe)
    return new_dataframes

def parse_isotherm_file(filename):
    with open(filename, encoding='utf-16') as f:
        content = f.read()
    sample_info = {}

    def safe_search(pattern, text, default='Не найдено'):
        match = re.search(pattern, text)
        return match.group(1) if match else default

    sample_info['Sample'] = safe_search(r'Sample:\s+(.*?)\s*(?:\n|$)', content)
    sample_info['Started'] = safe_search(r'Started:\s+([^\n]+?)\s+Analysis', content)
    sample_info['Completed'] = safe_search(r'Completed:\s+([^\n]+?)\s+Analysis', content)
    sample_info['Sample mass'] = safe_search(r'Sample mass:\s+([^\s]+)\s+g', content)

    def parse_isotherm():
        pattern = rf'Relative Pressure \(p/p°\)\s+Quantity Adsorbed \(mmol/g\)[\s\S]+?((?:\d+\.\d+\s+\d+\.\d+\n)+)'
        match = re.findall(pattern, content)
        if len(match) > 0:
            lines = match[0]
            data = []
            for line in lines.split('\n'):
                if line:
                    data.append(list(map(float, line.split())))
            df_adsorption = pd.DataFrame(data, columns=['p/p0', 'Quantity Adsorbed (mmol/g)'])
        else:
            print(f'ADSORPTION OF {filename} NOT FOUND')
            df_adsorption = None

        if len(match) == 2:
            lines = match[1]
            data = []
            for line in lines.split('\n'):
                if line:
                    data.append(list(map(float, line.split())))
            df_desorption = pd.DataFrame(data, columns=['p/p0', 'Quantity Adsorbed (mmol/g)'])
        else:
            print(f'DESORPTION OF {filename} NOT FOUND')
            df_desorption = None
        return df_adsorption, df_desorption


    df_adsorption, df_desorption = parse_isotherm()
    return df_adsorption, df_desorption

def read_from_all_folders():
    dataframes = []
    folders = [f"\DATA{i}" for i in range(1, 84)]
    for folder in folders:
        folder_path = r"E:\Anton\изотермы" + folder
        try:
            txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
        except FileNotFoundError:
            print(f'Folder {folder} NOT FOUND')
            continue
        for file in txt_files:
            file_path = folder_path+"\\"+file
            df_adsorption, df_desorption = parse_isotherm_file(file_path)
            if df_adsorption is not None:
                dataframes.append([df_adsorption, df_desorption])
    return dataframes


def cut_distribution(pore_distribution_data, pressure, pore_widths, pore_size_cut_grid, pressure_cut_grid):
    pore_cut_size = pore_size_cut_grid[-1]
    start_pressure = pressure[0]
    for i in range(len(pressure_cut_grid)-1):
        if pressure_cut_grid[i] <= start_pressure < pressure_cut_grid[i+1]:
            pore_cut_size = pore_size_cut_grid[i]


    for i in range(len(pore_widths)):
        if pore_widths[i] < pore_cut_size:
            pore_distribution_data[i] = 0
        else:
            break
    return pore_distribution_data


def save_as_dataset(name, generate_distribution=False):
    path = f'../data/datasets/{name}.npz'
    pressures = np.load("../data/initial kernels/Pressure_Silica.npy")[:]
    pore_widths = np.load("../data/initial kernels/Size_Kernel_Silica_Adsorption.npy")

    ###  kernel for pore dist generation
    kernel = np.load("../data/initial kernels/Kernel_Silica_Adsorption.npy")[:, :-10]
    ###

    pore_size_cut_grid = np.array([0.863, 0.863, 0.902, 0.982, 1.061, 1.061, 1.061, 1.167,
                                   1.220, 1.220, 1.220, 1.273, 1.379, 1.432, 1.432, 1.564])
    pressure_cut_grid = np.array([1e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 2e-4, 4e-4,
                                  6e-4, 8e-4, 1e-3, 2e-3, 4e-3, 6e-3, 8e-3, 1e-2])
    def find_nearest_idx(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    dataframes = read_from_all_folders()  # read txt (smp) files from DATA{i} folders
    dataframes = filter_isotherms(dataframes)

    dataset_size = len(dataframes)
    isotherm_data = np.empty((dataset_size, pressures[:-10].size))
    pore_distribution_data = np.empty((dataset_size, pore_widths.size))


    for i, data in enumerate(dataframes):
        print(f"isotherm number {i} out of {dataset_size}")

        #data[0]['Quantity Adsorbed (mmol/g)'] -= min(data[0]['Quantity Adsorbed (mmol/g)'])

        isotherm = np.interp(pressures[:-10], data[0]['p/p0'], data[0]['Quantity Adsorbed (mmol/g)'])
        cut_idx_pressure = find_nearest_idx(pressures[:-10], data[0]['p/p0'][0])
        isotherm = isotherm[cut_idx_pressure:]

        cut_size = np.interp(data[0]['p/p0'][0], pressure_cut_grid, pore_size_cut_grid)
        cut_size_idx= find_nearest_idx(pore_widths, cut_size)
        if generate_distribution:
            psd = fit_linear(adsorption=isotherm, kernel=kernel[cut_size_idx:, cut_idx_pressure:], alpha=0).x
            pore_distribution_data[i][cut_size_idx:] = psd
            pore_distribution_data[i][:cut_size_idx] = np.zeros(shape=cut_size_idx)

            isotherm_data[i][:cut_idx_pressure] = np.zeros(shape=cut_idx_pressure)
            isotherm_data[i][cut_idx_pressure:] = isotherm
        else:
            pore_distribution_data[i] = None
    with open(path, "wb") as f:
        np.savez_compressed(f, isotherm_data=isotherm_data,
                            pore_distribution_data=pore_distribution_data)


save_as_dataset("SMP_CUT_ALL_KERNEL_2", generate_distribution=True)