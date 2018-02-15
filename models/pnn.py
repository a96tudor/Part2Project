import numpy as np
import pandas as pd
from data import utils
from models import general as gng


class ProbabilisticNeuralNetwork:

    def __init__(self, data_path, evaluate=False):
        """
                CONSTRUCTOR

        :param data_path:        Path to the csv file containing the data
        :param evaluate:         Whether we want to evaluate the model or just to use this as a classifier
                                    Default False
        """
        self._data_path = data_path
        self._mode = 'EVALUATE' if evaluate else 'CLASSIFY'
        if evaluate:
            self._trainXs, self._trainYs, self._testXs, self._testYs = \
                utils.read_data_from_csv(data_path, gng.LABEL_COLS, split=True)
        else:
            self._Xs, self._Ys = utils.read_data_from_csv(data_path, gng.LABEL_COLS, split=False)

    def renew_split(self, percentile=.75):
        """
            Method that renews the current split on the data used by the model

        :param percentile:      How many entries should be in the train part
        :return:                -
        """
        full_train = pd.concat([self._trainXs, self._trainYs], axis=1)
        full_test = pd.concat([self._testXs, self._testYs], axis=1)

        full_df = pd.concat([full_train, full_test], axis=0)

        self._trainXs, self._trainYs, self._testXs, self._testYs = \
            utils.split_dataframe(full_df, gng.LABEL_COLS, percentile=percentile)

    