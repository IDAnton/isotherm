import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


def calculate_error(isotherm_real, restored_isotherm):
    defined_error = np.sum(np.abs(restored_isotherm - isotherm_real) / isotherm_real) / len(isotherm_real)
    return defined_error


def calculate_roughness(psd, ord=2):
    return np.linalg.norm(psd, ord=ord)



def test_model_predictions(prediction, x_test, kernel):
    error_lst = []
    roughness_lst = []
    for i in range(len(prediction)):
        restored_isotherm = np.dot(kernel.T, prediction[i])
        error_lst.append(calculate_error(restored_isotherm, np.array(x_test[i]))*100)
        roughness_lst.append(calculate_roughness(prediction[i]))
    return error_lst, roughness_lst


def calculate_error_for_math(x_test, restored_isotherms):
    error_math = []
    roughness_math = []
    for i in range(len(x_test)):
        error_math.append(calculate_error(restored_isotherms[i], np.array(x_test[i])) * 100)
        roughness_math.append(calculate_roughness(restored_isotherms[i]))
    return error_math, roughness_math


def calculate_kde_data(error_lst, start=0, stop=125, num=1000):
    x = np.linspace(start, stop, num)
    kde_error = gaussian_kde(error_lst)
    return x, kde_error(x), kde_error


def plot_testing_graphs(prediction_list, x_list, restored_isotherms, kernel, model_name_list):
    figure, axis = plt.subplots(2, 1)
    for i in range(len(prediction_list)):
        prediction = prediction_list[i]
        x = x_list[i]
        model_name = model_name_list[i]
        error_lst, roughness_lst = test_model_predictions(prediction, x, kernel=kernel.T)
        kde_x, kde_error, kde_fun = calculate_kde_data(error_lst, stop=150)
        kde_x_r, kde_roughness, _ = calculate_kde_data(roughness_lst, stop=150)

        axis[0].plot(kde_x, kde_error, label=model_name)
        axis[0].scatter(error_lst, kde_fun(error_lst))
        axis[1].plot(kde_x_r, kde_roughness, label=model_name)

        print(f"{model_name} Error PDF median: {np.median(error_lst):.3f}")
        print(f"{model_name} Roughness PDF median: {np.median(roughness_lst):.3f}")

    error_lst_math, roughness_lst_math = calculate_error_for_math(x_list[0], restored_isotherms=restored_isotherms)
    kde_x_math, kde_error_math, kde_fun_math = calculate_kde_data(error_lst_math, stop=150)
    kde_x_math_r, kde_roughness_math, _ = calculate_kde_data(roughness_lst_math, stop=150)
    axis[1].plot(kde_x_math_r, kde_roughness_math, label="math")
    axis[0].plot(kde_x_math, kde_error_math, label="math")
    axis[0].scatter(error_lst_math, kde_fun_math(error_lst_math))

    print(f"math Error PDF median: {np.median(error_lst_math):.3f}")
    print(f"math Roughness PDF median: {np.median(roughness_lst_math):.3f}")

    axis[0].grid(True)
    axis[1].grid(True)
    axis[0].legend()
    axis[1].legend()

    axis[0].set_title(f"Error PDF")
    axis[0].title.set_size(10)
    axis[1].set_title(f"Roughness PDF")
    axis[1].title.set_size(10)
    plt.show()
