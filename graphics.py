import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import data.training.constants as cnst
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
from scipy.stats import binom


def piechart_dataset_distribution(dataset_path):
    """

            Method that prints a histogram of the distribution of node types
        present in our dataset

    :param dataset_path:
    :return:
    """

    df = pd.read_csv(dataset_path)

    labels = cnst.CODE_TO_NODE.values()
    sizes = [len(df[df['NODE_TYPE'] == code]) for code in cnst.CODE_TO_NODE]

    colors = ['yellowgreen', 'lightcoral', 'lightskyblue']
    explode = [0.1, 0.0, 0.0]

    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=False)

    plt.title("Node type distribution in the dataset")

    plt.savefig("data/graphics/img/pie_node_types.png")


def activation_functions_plot():

    Xs = np.random.uniform(low=-5.0, high=5.0, size=10000)
    Xs = sorted(Xs)

    Ys_tanh = np.tanh(Xs)

    relu = np.vectorize(lambda x: abs(x) * (x > 0))
    lrelu = np.vectorize(lambda x: 0.005*x if x < 0 else x)

    Ys_relu = relu(Xs)
    Ys_lrelu = lrelu(Xs)

    plt.subplot(211)

    tanh, = plt.plot(Xs, Ys_tanh, label='tanh')
    relu, = plt.plot(Xs, Ys_relu, label='relu')
    lrelu, = plt.plot(Xs, Ys_lrelu, '--', label='lrelu')

    plt.legend(
        [tanh, relu, lrelu],
        ['tanh', 'ReLU', 'LReLU']
    )

    plt.xlabel('Input x')
    plt.ylabel('σ(x)')


    Ys_dtanh = 1.0 - Ys_tanh**2

    drelu = np.vectorize(lambda x: 0 if x < 0 else 1)
    dlrelu = np.vectorize(lambda x: 0.005 if x < 0 else 1)

    Ys_drelu = drelu(Xs)
    Ys_dlrelu = dlrelu(Xs)

    plt.subplot(212)

    dtanh, = plt.plot(Xs, Ys_dtanh)
    drelu, = plt.plot(Xs, Ys_drelu)
    dlrelu, = plt.plot(Xs, Ys_dlrelu, "--")

    plt.legend(
        [dtanh, drelu, dlrelu],
        ['tanh', 'ReLU', 'LReLU']
    )

    plt.xlabel('Input x')
    plt.ylabel('Derivative of σ(x)')

    plt.gca().yaxis.set_minor_formatter(NullFormatter())

    plt.tight_layout()

    plt.show()

