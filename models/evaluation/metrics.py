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
import keras.backend as K


def recall(y_true, y_pred):
    """
        Function that computes the recall of a model
        Follows the formula:

                           tp
                recall = -------
                         (tp+fn)

    :param y_true:        The test set classes
    :param y_pred:        The predicted classes
    :return:              The corresponding classes, as tf.Tensor
    """
    tp = true_positives(y_true, y_pred)
    fn = false_negatives(y_true, y_pred)

    recall = float(tp / (tp+fn))

    return recall


def precision(y_true, y_pred):
    """
        Function that computes the precision of a model
        Follows the formula:

                           tp
                recall = -------
                         (tp+fp)

    :param y_true:        The test set classes
    :param y_pred:        The predicted classes
    :return:              The corresponding precision, as tf.Tensor
    """
    tp = true_positives(y_true, y_pred)
    fp = false_positives(y_true, y_pred)

    precision = float(tp / (tp+fp))

    return precision


def false_negatives(y_true, y_pred):
    """
        Function that returns the number of false negatives.
        Follows the formula:

            fn = count(i where y_true[i] = 'SHOW' and y_pred[i] = 'HIDE')

    :param y_true:        The test set classes
    :param y_pred:        The predicted classes
    :return:              The corresponding false negatives count, as tf.Tensor
    """
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos

    y_pos = K.round(K.clip(y_true, 0, 1))

    fn = K.sum(y_pred_neg * y_pos)

    return fn


def false_positives(y_true, y_pred):
    """
        Function that returns the number of false positives.
        Follows the formula:

            fp = count(i where y_true[i] = 'HIDE' and y_pred[i] = 'SHOW')

    :param y_true:        The test set classes
    :param y_pred:        The predicted classes
    :return:              The corresponding false positives count, as tf.Tensor
    """
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))

    y_pos = K.round(K.clip(y_true, 0, 1))
    y_neg = 1 - y_pos

    fp = K.sum(y_neg * y_pred_pos)

    return fp


def true_negatives(y_true, y_pred):
    """
        Function that returns the number of true negatives.
        Follows the formula:

            tn = count(i where y_true[i] = 'HIDE' and y_pred[i] = 'HIDE')

    :param y_true:        The test set classes
    :param y_pred:        The predicted classes
    :return:              The corresponding true negatives count, as tf.Tensor
    """
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos

    y_pos = K.round(K.clip(y_true, 0, 1))
    y_neg = 1 - y_pos

    tn = K.sum(y_neg * y_pred_neg)

    return tn


def true_positives(y_true, y_pred):
    """
        Function that returns the number of true positives.
        Follows the formula:

            tn = count(i where y_true[i] = 'SHOW' and y_pred[i] = 'SHOW')

    :param y_true:        The test set classes
    :param y_pred:        The predicted classes
    :return:              The corresponding true positives count, as tf.Tensor
    """
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))

    y_pos = K.round(K.clip(y_true, 0, 1))

    tp = K.sum(y_pos * y_pred_pos)

    return tp


def mcc(y_true, y_pred):
    """
        Function that computes the MCC score for a given model
        Follows the formula:

                                        tp * tn - tp * fn
                mcc = ------------------------------------------------------
                       sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

    :param y_true:        The test set results
    :param y_pred:        The predicted results
    :return:              The corresponding MCC score
    """
    tp = true_positives(y_true, y_pred)
    tn = true_negatives(y_true, y_pred)

    fp = false_positives(y_true, y_pred)
    fn = false_negatives(y_true, y_pred)

    numerator = (tp * tn - fp * fn)
    denominator = K.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

    return numerator / (denominator + K.epsilon())


def f1(y_true, y_pred):
    """
        Function that computes the F1 score for a givven model
        Follows the formula:

                            precision * recall
                f1 = 2 * ------------------------
                            precision + recall

    :param y_true:        The test set results
    :param y_pred:        The predicted results
    :return:              The f1 score
    """
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)

    f1 = 2 * ((p * r) / (p + r))

    return f1


def accuracy(y_true, y_pred):
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
    correct_pred = K.sum(y_true * y_pred)

    return correct_pred / len(y_pred)

