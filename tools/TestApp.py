import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import matplotlib.ticker as ticker
from generator import Generator
import inverse

# import keras
# import tensorflow as tf


class App:
    def __init__(self, model=None, gen=None):
        self.gen = gen
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, label="isotherm")
        self.ax2 = self.fig.add_subplot(111, label="distribution", frame_on=False)
        self.ax3 = self.fig.add_subplot(111, label="prediction", frame_on=False)
        self.ax3.xaxis.set_major_locator(ticker.NullLocator())
        self.ax3.yaxis.set_major_locator(ticker.NullLocator())
        self.ax.xaxis.tick_top()
        self.ax.yaxis.tick_right()

        self.isotherm_line, = self.ax.plot(gen.pressures_s, np.zeros_like(gen.pressures_s),
                                           lw=2, marker='.', label="isotherm")
        self.restored_isotherm_line, = self.ax.plot(gen.pressures_s, np.zeros_like(gen.pressures_s),
                                           lw=2, marker='.', label="restored isotherm")
        self.distribution_line, = self.ax2.plot(gen.a_array, np.zeros_like(gen.a_array),
                                                lw=2, color="orange", marker='.', label="distribution line")
        self.prediction_line, = self.ax3.plot(gen.a_array, np.zeros_like(gen.a_array),
                                              lw=2, color="red", marker='.', label="prediction line")

        self.model = model
        self.d0_1 = 5
        self.d0_2 = 10
        self.sigma1 = 1
        self.sigma2 = 1
        self.a = 0.8
        self.alpha = 0.0
        self.beta = 0.0

        self.kernel = np.load("../data/initial kernels/Kernel_Silica_Adsorption.npy")
        self.pore_width = np.load("../data/initial kernels/Size_Kernel_Silica_Adsorption.npy")
        cut_kernel = []
        for i in range(len(self.kernel)):
            cut_kernel.append(self.kernel[i][40:458])
        self.cut_kernel = np.array(cut_kernel)

        self.visualizeGraph()

        graphBox1 = self.fig.add_axes([0.1, 0.02, 0.05, 0.03])
        graphBox2 = self.fig.add_axes([0.2, 0.02, 0.05, 0.03])
        graphBox3 = self.fig.add_axes([0.3, 0.02, 0.05, 0.03])
        graphBox4 = self.fig.add_axes([0.4, 0.02, 0.05, 0.03])
        graphBox5 = self.fig.add_axes([0.5, 0.02, 0.05, 0.03])
        graphBox6 = self.fig.add_axes([0.6, 0.02, 0.05, 0.03])
        graphBox7 = self.fig.add_axes([0.7, 0.02, 0.05, 0.03])
        graphBoxButton = self.fig.add_axes([0.8, 0.02, 0.05, 0.03])
        ButtonBox = Button(graphBoxButton, 'process')
        txtBox1 = TextBox(graphBox1, "intensity")
        txtBox2 = TextBox(graphBox2, "d0_1")
        txtBox3 = TextBox(graphBox3, "d0_2")
        txtBox4 = TextBox(graphBox4, "sigma1")
        txtBox5 = TextBox(graphBox5, "sigma2")
        txtBox6 = TextBox(graphBox6, "a")
        txtBox7 = TextBox(graphBox7, "b")
        txtBox1.on_submit(self.change_a)
        txtBox2.on_submit(self.change_d01)
        txtBox3.on_submit(self.change_d02)
        txtBox4.on_submit(self.change_sigma1)
        txtBox5.on_submit(self.change_sigma2)
        txtBox6.on_submit(self.change_alpha)
        txtBox7.on_submit(self.change_beta)
        ButtonBox.on_clicked(self.visualizeGraph)
        txtBox1.set_val(self.a)
        txtBox2.set_val(self.d0_1)
        txtBox3.set_val(self.d0_2)
        txtBox4.set_val(self.sigma1)
        txtBox5.set_val(self.sigma2)
        txtBox6.set_val(self.alpha)
        txtBox7.set_val(self.beta)

        plt.legend()
        plt.show()

    def visualizeGraph(self, *args, **kwargs):
        self.gen.generate_pore_distribution_2_peaks(d0_1=self.d0_1, d0_2=self.d0_2, sigma1=self.sigma1, sigma2=self.sigma2,
                                            a=self.a)

        self.gen.calculate_isotherms()

        # pre process data
        # data_to_net = self.gen.n_s[40:458] - min(self.gen.n_s[40:458])
        # data_to_net = data_to_net / max(data_to_net)
        #

        #fit = self.model.predict(np.array([data_to_net])).T
        #fit = fit / max(fit)
        fit = inverse.fit_SLSQP(adsorption=self.gen.n_s[40:458], kernel=self.cut_kernel, a_array=self.pore_width, alpha=self.alpha, beta=self.beta).x
        self.restored_isotherm = np.dot(self.kernel.T, fit)

        self.isotherm_line.set_ydata(self.gen.n_s)
        self.distribution_line.set_ydata(self.gen.pore_distribution)
        self.prediction_line.set_ydata(fit)
        self.restored_isotherm_line.set_ydata(self.restored_isotherm)
        self.ax.relim()
        self.ax2.relim()
        self.ax3.relim()
        self.ax.autoscale_view()
        self.ax2.autoscale_view()
        self.ax3.autoscale_view()
        plt.legend()
        plt.draw()

    def change_a(self, *args, **kwargs):
        self.a = float(args[0])

    def change_d01(self, *args, **kwargs):
        self.d0_1 = float(args[0])

    def change_d02(self, *args, **kwargs):
        self.d0_2 = float(args[0])

    def change_sigma1(self, *args, **kwargs):
        self.sigma1 = float(args[0])

    def change_sigma2(self, *args, **kwargs):
        self.sigma2 = float(args[0])

    def change_alpha(self, *args, **kwargs):
        self.alpha = float(args[0])

    def change_beta(self, *args, **kwargs):
        self.beta = float(args[0])


if __name__ == "__main__":
    gen = Generator(path_s="../data/initial kernels/Kernel_Silica_Adsorption.npy",
                    path_d="../data/initial kernels/Kernel_Silica_Desorption.npy",
                    path_p_d="../data/initial kernels/Pressure_Silica.npy",
                    path_p_s="../data/initial kernels/Pressure_Silica.npy",
                    path_a="../data/initial kernels/Size_Kernel_Silica_Adsorption.npy"
                    )
    #model = keras.models.load_model('../data/models/silica_medium_relu.keras', custom_objects={'abs': tf.math.abs})
    App(gen=gen)
