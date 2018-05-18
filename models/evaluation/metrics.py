"""
Part2Project -- metrics.py

Copyright Mar 2018 [Tudor Mihai Avram]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
from sklearn.metrics import confusion_matrix, accuracy_score
import numpy as np


def get_confusion_matrix(y_true: np.ndarray,
                         y_pred: np.ndarray) -> list:
    """
        Method that takes the predicted and true values and
        returns the 4 elements of the confusion matrix in
        the following order:

                1. true positives
                2. true negatives
                3. false positives
                4. false negatives

    :param y_true:      The test set classes
    :param y_pred:      The predicted classes

    :return:            The corresponding values
    """

    tn, fp, fn, tp = confusion_matrix(y_pred=y_pred, y_true=y_true).ravel()

    return [tp, tn, fp, fn]


def accuracy(y_true: np.ndarray,
             y_pred: np.ndarray) -> float:
    """
        Function that computes the accuracy of a model
        Follows the formula:

                                count(i where y_true[i] == y_pred[i])
                accuracy =  --------------------------------------------
                                            len(y_true)

    :param y_true:        The test set results
    :param y_pred:        The predicted results
    :return:              The corresponding accuracy
    """

    return accuracy_score(y_true, y_pred)

