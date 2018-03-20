import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import data.training.constants as cnst


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

piechart_dataset_distribution("data/training/training_set.csv")
