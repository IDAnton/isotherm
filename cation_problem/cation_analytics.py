from typing import List

import numpy as np
from matplotlib import pyplot as plt


def plot_cation_analytics(labels: np.array, cations: List,
                          cations_pair: List[str], title: str = None, no_swap=True) -> None:
    cation_data_analytics = []
    cat1 = cations_pair[0]
    cat2 = cations_pair[1]
    for i, c in enumerate(cations):
        if c == cations_pair:
            cat1_data = labels[i][:4]
            cat2_data = labels[i][4:]
            cation_data_analytics.append(np.concatenate((cat1_data / sum(cat1_data), cat2_data / sum(cat2_data))))
    cation_data_analytics = np.array(cation_data_analytics)
    cation_data_analytics = np.sum(cation_data_analytics, axis=0) / np.sum(cation_data_analytics)
    if no_swap:
        plt.scatter([f"s1 {cat1}", f"s1' {cat1}", f"s2 {cat1}", f"s3 {cat1}", f"s1 {cat2}", f"s1' {cat2}", f"s2 {cat2}",
                     f"s3 {cat2}"],
                    cation_data_analytics)
    else:
        plt.scatter([f"s1 {cat2}", f"s1' {cat2}", f"s2 {cat2}", f"s3 {cat2}", f"s1 {cat1}", f"s1' {cat1}", f"s2 {cat1}",
                     f"s3 {cat1}"],
                    np.concatenate((cation_data_analytics[4:], cation_data_analytics[:4])))
    plt.title(title)
    plt.show()
