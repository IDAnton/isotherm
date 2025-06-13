import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import numpy as np
import inverse

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Isotherm -> PSD")

        self.pore_widths = np.load("../data/initial kernels/Size_Kernel_Silica_Adsorption.npy")
        self.pressures = np.load("../data/initial kernels/Pressure_Silica.npy")[:]
        self.kernel = np.load("../data/initial kernels/Kernel_Silica_Adsorption.npy")[:, :]

        # Основной фрейм
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм с графиками слева
        plot_frame = tk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Фрейм с кнопками и дропбоксом справа
        control_frame = tk.Frame(main_frame, padx=10, pady=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Создаем два графика Matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(5, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Панель инструментов Matplotlib
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Данные по умолчанию
        self.isotherm = np.zeros((len(self.pressures[:])))
        self.PSD = np.zeros((len(self.pore_widths)))
        self.option = tk.StringVar(value="neural network")
        self.name = ""

        # Кнопки
        btn_load = tk.Button(control_frame, text="Загрузить изотерму", command=self.load_data)
        btn_load.pack(pady=5, fill=tk.X)

        btn_save = tk.Button(control_frame, text="Сохранить PSD", command=self.save_data)
        btn_save.pack(pady=5, fill=tk.X)

        # Дропбокс (Combobox)
        tk.Label(control_frame, text="Выберите модель построения PSD:").pack(pady=10)
        options = ["DFT", "neural network"]
        dropdown = ttk.Combobox(control_frame, textvariable=self.option, values=options, state="readonly")
        dropdown.pack(fill=tk.X)
        dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_plot())

        self.update_plot()

    def load_data(self):
        def find_nearest_idx(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return idx

        file_path = filedialog.askopenfilename(filetypes=[("txt", "*.txt")])
        self.name = (file_path.split("/")[-1]).replace(".txt", "")
        if file_path:
            isotherm = pd.read_csv(file_path, header=None)
            p_exp = isotherm.iloc[:, 1].to_numpy()
            n_s_exp_raw = isotherm.iloc[:, 3].to_numpy()
            cut_idx_pressure = find_nearest_idx(self.pressures, p_exp[0])
            n_s_exp = (np.interp(self.pressures, p_exp, n_s_exp_raw))
            n_s_exp[:cut_idx_pressure] = np.zeros(shape=cut_idx_pressure)
            self.isotherm = n_s_exp
            self.update_plot()

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("CSV файлы", "*.csv")])
        if file_path:
            self.data.to_csv(file_path, index=False)

    def update_plot(self):
        self.ax1.clear()
        self.ax2.clear()

        x = self.isotherm
        if self.option.get() == "DFT":
            self.PSD = inverse.fit_linear(self.isotherm, kernel=self.kernel, alpha=0).x
            print(self.isotherm.shape, self.kernel.shape)
        elif self.option.get() == "neural network":
            pass
        else:
            y = np.zeros(len(x))

        self.ax1.plot(self.pressures, self.isotherm, label=self.name, color='blue', marker=".")
        self.ax1.set_title("Изотерма")
        self.ax1.legend()
        self.ax1.grid(True)
        self.ax1.set_ylabel("Адсорбция, $см^3$(НТД)/$г$")
        self.ax1.set_xlabel("Давление, $P/P_{0}$")

        self.ax2.plot(self.pore_widths, self.PSD, color='green', marker=".")
        self.ax2.set_title("Распределение пор по размерам")
        self.ax2.grid(True)
        self.ax2.set_ylabel("Объем пор, $см^3$/$нм*г$")
        self.ax2.set_xlabel("Размер пор, $нм$")

        self.canvas.draw()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()
