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

def draw_cnn():
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    plt.rcdefaults()
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    from matplotlib.patches import Circle

    NumDots = 4
    NumConvMax = 8
    NumFcMax = 20
    White = 1.
    Light = 0.7
    Medium = 0.5
    Dark = 0.3
    Darker = 0.15
    Black = 0.

    def add_layer(patches, colors, size=(24, 24), num=5,
                  top_left=[0, 0],
                  loc_diff=[3, -3],
                  ):
        # add a rectangle
        top_left = np.array(top_left)
        loc_diff = np.array(loc_diff)
        loc_start = top_left - np.array([0, size[0]])
        for ind in range(num):
            patches.append(Rectangle(loc_start + ind * loc_diff, size[1], size[0]))
            if ind % 2:
                colors.append(Medium)
            else:
                colors.append(Light)

    def add_layer_with_omission(patches, colors, size=(24, 24),
                                num=5, num_max=8,
                                num_dots=4,
                                top_left=[0, 0],
                                loc_diff=[3, -3],
                                ):
        # add a rectangle
        top_left = np.array(top_left)
        loc_diff = np.array(loc_diff)
        loc_start = top_left - np.array([0, size[0]])
        this_num = min(num, num_max)
        start_omit = (this_num - num_dots) // 2
        end_omit = this_num - start_omit
        start_omit -= 1
        for ind in range(this_num):
            if (num > num_max) and (start_omit < ind < end_omit):
                omit = True
            else:
                omit = False

            if omit:
                patches.append(
                    Circle(loc_start + ind * loc_diff + np.array(size) / 2, 0.5))
            else:
                patches.append(Rectangle(loc_start + ind * loc_diff,
                                         size[1], size[0]))

            if omit:
                colors.append(Black)
            elif ind % 2:
                colors.append(Medium)
            else:
                colors.append(Light)

    def add_mapping(patches, colors, start_ratio, end_ratio, patch_size, ind_bgn,
                    top_left_list, loc_diff_list, num_show_list, size_list):

        start_loc = top_left_list[ind_bgn] \
                    + (num_show_list[ind_bgn] - 1) * np.array(loc_diff_list[ind_bgn]) \
                    + np.array([start_ratio[0] * (size_list[ind_bgn][1] - patch_size[1]),
                                - start_ratio[1] * (size_list[ind_bgn][0] - patch_size[0])]
                               )

        end_loc = top_left_list[ind_bgn + 1] \
                  + (num_show_list[ind_bgn + 1] - 1) * np.array(
            loc_diff_list[ind_bgn + 1]) \
                  + np.array([end_ratio[0] * size_list[ind_bgn + 1][1],
                              - end_ratio[1] * size_list[ind_bgn + 1][0]])

        patches.append(Rectangle(start_loc, patch_size[1], -patch_size[0]))
        colors.append(Dark)
        patches.append(Line2D([start_loc[0], end_loc[0]],
                              [start_loc[1], end_loc[1]]))
        colors.append(Darker)
        patches.append(Line2D([start_loc[0] + patch_size[1], end_loc[0]],
                              [start_loc[1], end_loc[1]]))
        colors.append(Darker)
        patches.append(Line2D([start_loc[0], end_loc[0]],
                              [start_loc[1] - patch_size[0], end_loc[1]]))
        colors.append(Darker)
        patches.append(Line2D([start_loc[0] + patch_size[1], end_loc[0]],
                              [start_loc[1] - patch_size[0], end_loc[1]]))
        colors.append(Darker)

    def label(xy, text, xy_off=[0, 4]):
        plt.text(xy[0] + xy_off[0], xy[1] + xy_off[1], text,
                 family='sans-serif', size=8)

    if __name__ == '__main__':

        fc_unit_size = 2
        layer_width = 40
        flag_omit = True

        patches = []
        colors = []

        fig, ax = plt.subplots()

        ############################
        # conv layers
        size_list = [(23, 1), (32, 1), (64, 1), (128, 1), (256, 1)]
        num_list = [3, 32, 32, 48, 48]
        x_diff_list = [0, layer_width, layer_width, layer_width, layer_width]
        text_list = ['Inputs'] + ['Feature\nmaps'] * (len(size_list) - 1)
        loc_diff_list = [[3, -3]] * len(size_list)

        num_show_list = list(map(min, num_list, [NumConvMax] * len(num_list)))
        top_left_list = np.c_[np.cumsum(x_diff_list), np.zeros(len(x_diff_list))]

        add_layer(patches, colors, size=(23, 1), num=32)


        plt.tight_layout()
        plt.axis('equal')
        plt.axis('off')
        plt.show()
        fig.set_size_inches(8, 2.5)

        fig_dir = './'
        fig_ext = '.png'
        fig.savefig(os.path.join(fig_dir, 'convnet_fig' + fig_ext),
                    bbox_inches='tight', pad_inches=0)

draw_cnn()