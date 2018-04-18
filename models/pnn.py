import numpy as np
import pandas as pd
from data import utils
import strings
from models.model import Model
from models.exceptions import InvalidModeError
from data.features.constants import *


class ProbabilisticNeuralNetwork(Model):

    def __init__(self,
                 data_path,
                 evaluate=False):
        """
                CONSTRUCTOR

        :param data_path:        Path to the csv file containing the data
        :param evaluate:         Whether we want to evaluate the model or just to use this as a classifier
                                    Default False
        """
        super().__init__()

        self._data_path = data_path
        self._mode = 'EVALUATE' if evaluate else 'CLASSIFY'
        if evaluate:
            self._trainXs, self._trainYs, self._testXs, self._testYs = \
                utils.read_data_from_csv(data_path, LABELS, drop_cols=None, split=True)

            self.print_msg(
                (
                    strings.HEADLINE_PNN, "", "Data loaded!",
                    ("%d Train examples", len(self._trainXs)),
                    ("%d Test examples", len(self._testXs)),
                )
            )

        else:
            self._Xs, self._Ys = utils.read_data_from_csv(data_path, LABELS, split=False)
            self.print_msg(
                (
                    strings.HEADLINE_PNN, "", "Data loaded!",
                    ("%d Examples in the training set", len(self._Xs))
                )
            )

    def renew_split(self, test_part, percentile=.75):
        """
            Method that renews the current split on the data used by the model

        :param percentile:      How many entries should be in the train part
        :param test_part:       The test_part^th (1-percentile) section of the df will be used as the test set
        :return:                -
        """
        full_train = pd.concat([self._trainXs, self._trainYs], axis=1)
        full_test = pd.concat([self._testXs, self._testYs], axis=1)

        full_df = pd.concat([full_train, full_test], axis=0, ignore_index=True)

        print("**%d**" % len(full_df))

        self._trainXs, self._trainYs, self._testXs, self._testYs = \
            utils.split_dataframe(full_df, LABELS, test_part=test_part, percentile=percentile)

        print("New data split!")
        print("%d TrainX %d TrainY" % (len(self._trainXs), len(self._trainYs)))
        print("%d TestX %d TestY" % (len(self._testXs), len(self._testYs)))

    def evaluate(self):
        """
                    Method that evaluates the model. Only available in 'EVALUATE' mode
        :return:
        :raises InvalidModeError:       if it is not in evaluate mode
        """
        if self._mode != 'EVALUATE':
            raise InvalidModeError("Invalid mode. Is %s, should be 'EVALUATE'" % self._mode)

        self.print_msg(("", strings.LINE_DELIMITER, "STARTED EVALUATION"))

        trainX_class1_DF = self._trainXs[self._trainYs['SHOW'] == 1]
        trainX_class2_DF = self._trainXs[self._trainYs['HIDE'] == 1]

        c1Xs = trainX_class1_DF.as_matrix()
        c2Xs = trainX_class2_DF.as_matrix()

        testXs = self._testXs.as_matrix()

        print(self._testYs.columns.values)

        self.print_msg(("", "Splited data into 'SHOW' and 'HIDE' nodes",
                        ("     %.6f labelled as SHOW", (len(trainX_class1_DF)/ len(self._trainXs))),
                        ("     %.6f labelled as HIDE", (len(trainX_class2_DF))/ len(self._trainXs))))

        print("Starting to calculate the exponentials")

        exp_c1 = [
            [
                np.exp(
                    - np.sum(
                        [
                            ((test_value[idx] - c1X[idx]) ** 2) * 0.5
                            for idx in range(len(test_value))
                        ]
                    )
                ) for c1X in c1Xs
            ] for test_value in testXs
        ]

        print("Finished for 1st class...")

        exp_c2 = [
            [
                np.exp(
                    - np.sum(
                        [
                            ((test_value[idx] - c2X[idx]) ** 2) * 0.5
                            for idx in range(len(test_value))
                        ]
                    )
                ) for c2X in c2Xs
            ] for test_value in testXs
        ]

        Y1s = [np.sum(exp_y1) / (1.0 * len(c1Xs)) for exp_y1 in exp_c1]
        Y2s = [np.sum(exp_y2) / (1.0 * len(c2Xs)) for exp_y2 in exp_c2]

        print("Done calculating exponentials")

        results = [
            {
                "SHOW": Y1s[idx] >= Y2s[idx],
                "HIDE": Y2s[idx] > Y1s[idx]
            } for idx in range(len(Y1s))
        ]

        print("====================================")
        print("Got final results!")
        print("%d entries in the results list" % len(results))
        print("%.6f classed as HIDE" % float((sum([1 if result["HIDE"] else 0 for result in results]) / len(results))))
        print("%.6f classed as SHOW" % float((sum([1 if result["SHOW"] else 0 for result in results]) / len(results))))
        print("===========================")

        print("Now performing the actual evaluation")

        return self.get_stats(results, self._testYs)