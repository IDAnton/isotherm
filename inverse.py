import numpy as np
import scipy
from scipy import optimize
from scipy.optimize import lsq_linear


def fit_SLSQP(adsorption, kernel, alpha=0, beta=0, a_array=None):
    def kernel_loading(pore_dist):
        return np.multiply(
            kernel,
            pore_dist[:, np.newaxis]
        ).sum(axis=0)

    def sum_squares(pore_dist):
        return (np.square(
            np.subtract(
                kernel_loading(pore_dist),
                adsorption)).sum(axis=0) + alpha * np.sum(pore_dist * np.log(pore_dist)) +
                beta * np.sum(np.square(np.diff(pore_dist)/a_array[:-1])))

    cons = [{
        'type': 'ineq',
        'fun': lambda x: x,
    }]
    guess = np.array([0.001 for _ in range(len(kernel))])
    bounds = [(0, None) for _ in range(len(kernel))]
    result = optimize.minimize(
        sum_squares,
        guess,
        method='SLSQP',
        bounds=bounds,
        constraints=cons,
        options={'ftol': 1e-04, 'maxiter': 300}
    )
    return result


def fit_SLSQP_both_branches(adsorption, desorption, kernel_adsorption, kernel_desorption, beta=0, a_array=None):
    def kernel_loading(pore_dist, kernel):
        return np.multiply(
            kernel,
            pore_dist[:, np.newaxis]
        ).sum(axis=0)

    def sum_squares(pore_dist):
        return (np.square(
            np.subtract(
                kernel_loading(pore_dist, kernel_adsorption),
                adsorption)).sum(axis=0) +
            np.square(np.subtract(
                    kernel_loading(pore_dist, kernel_desorption),
                    desorption)).sum(axis=0) +

                beta * np.sum(np.square(np.diff(pore_dist)/a_array[:-1])))

    cons = [{
        'type': 'ineq',
        'fun': lambda x: x,
    }]
    guess = np.array([0.001 for _ in range(len(kernel_adsorption))])
    bounds = [(0, None) for _ in range(len(kernel_adsorption))]
    result = optimize.minimize(
        sum_squares,
        guess,
        method='SLSQP',
        bounds=bounds,
        constraints=cons,
        options={'ftol': 1e-04, 'maxiter': 300}
    )
    return result


def fit_linear(adsorption, kernel, alpha):
    A_augmented = np.vstack([kernel.T, np.sqrt(alpha) * np.eye(len(kernel))])
    b_augmented = np.concatenate([adsorption, np.zeros(len(kernel))])
    result = lsq_linear(A_augmented, b_augmented, bounds=(0, np.inf))
    return result
