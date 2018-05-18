import numpy as np
import pandas as pd
from data import utils
import strings
from models.model import Model
from data.features.constants import *
from models.config import *
from pickle import dump, load

from data.utils import read_csv, split_dataframe, dump_json, get_new_filename_in_dir

class ProbabilisticNeuralNetwork(Model):
    """
        Class representing the Probabilistic Neural Network
    """

    def __init__(self,
                 config: ModelConfig):

        """
            Constructor

        :param config:      The configuration for the model
        """
        super(ProbabilisticNeuralNetwork, self).__init__(config)

        self.weights = None
        self.As = None
        self.sigma = None
        self.name = 'pnn'

    def _normalize(self,
                   array: np.ndarray):
        """
            Private method that takes a numpy array and normalizez it such as ||a|| = 1

        :param array:       The np.ndarray to normalize
        :return:            The normalized np.ndarray
        """
        factor = np.sqrt(
            np.sum(array ** 2)
        )

        return np.array(array / factor)

    def _product_with_weight(self,
                             X: np.ndarray,
                             idx: int):
        """

        :param X:           The vector to multiply the weight with
        :param idx:         The weight index
        :return:            The resulting product
        """
        return - np.sum(
            [
                ((X[i] - self.weights[idx, i]) ** 2) * 0.5
                for i in range(len(X))
            ]
        )

    def _get_parzen_estimates(self,
                              data: np.ndarray) -> np.ndarray:
        """
            Private method that, based on a set of input feature vectors

        :param data:      The list of feature vectors to process
        :return:          The corresponding Parzen estimates
        """

        results = np.empty(
            shape=(len(data), len(self.config.LABELS)),
            dtype=float
        )

        for i in range(len(data)):
            X = data[i, :]
            g_SHOW = 0.0
            g_HIDE = 0.0
            for j in range(len(self.weights)):
                z = self._product_with_weight(X, j)
                exp = 1/(np.sqrt(2*np.pi)) * np.exp(z)
                g_SHOW += self.As[j, 0] * exp
                g_HIDE += self.As[j, 1] * exp

            results[i, :] = np.array([g_SHOW, g_HIDE])

        return results

    def load_checkpoint(self,
                        path: str) -> None:
        """
            Method used to load a pre-trained checkpoint for the given
        :return:
        """
        file1 = path + "/weights.pkl"
        file2 = path + "/As.pkl"
        file3 = path + "/sigma.pkl"

        def get(file):
            with open(file, 'rb') as fout:
                data = load(fout)
            return data

        self.weights = get(file1)
        self.As = get(file2)
        self.sigma = get(file3)

    def save_checkpoint(self,
                        path: str) -> None:
        """
            Method that saves a pre-trained checkpoint of the model

        :param path:    Path to the directory where to save the model parameters

        :return: -
        """
        file1 = path + "/weights.pkl"
        file2 = path + "/As.pkl"
        file3 = path + "/sigma.pkl"

        def save(file, data):
            with open(file, 'wb') as fout:
                dump(data, fout)

        save(file1, self.weights)
        save(file2, self.As)
        save(file3, self.sigma)

    def setup(self,
              input_dim: tuple,
              **kwargs):

        if isinstance(self.config, PredictConfig):
            self.load_checkpoint()
        else:
            return

    def train(self,
              trainX,
              trainY,
              validateX,
              validateY,
              save_checkpoint: bool = False):
        """
            Method used in training the model based
            on a provided dataset

        :param trainX:
        :param trainY:
        :param validateX:
        :param validateY:
        :param save_checkpoint:     Whether to save the checkpoint after training or not.
                                    Only available during running in TrainingConfig configuration

        :return:                    -
        """
        assert self.config in (TrainConfig, EvalConfig, )
        assert self.config == TrainConfig or not save_checkpoint

        if validateX is not None or validateY is not None:
            print("Warning: The PNN does not require a validation set! Just ignoring it for now.")

        self.weights = np.empty(
            shape=trainX.shape,
            dtype=float
        )

        self.As = np.empty(
            shape=trainY.shape,
            dtype=int
        )

        for i in range(len(trainX)):

            self.weights[i, :] = trainX[i, :]
            self.As[i, :] = trainY[i, :]

        sigmas = [2*np.sum(trainY[:, 0])**2, 2*np.sum(trainY[:, 1])**2]
        self.sigma = np.array(sigmas)

        self.built = True

        if save_checkpoint:
            self.save_checkpoint(
                path=self.config.CHECKPOINTS_PATH + "/pnn"
            )

    def predict_class(self,
                      data: np.ndarray) -> np.ndarray:
        """
            Method used to predict the class for a set of input feature vectors.
            The predicted class will be argmax(g_c), where c is one of 'SHOW' or 'HIDE'
            and g_c is the Parzen estimate for class c given a feature vector x

        :param data:        the data used for prediction
        :return:            a list of predicted classes
        """

        parzen_est = self._get_parzen_estimates(data)

        classes = np.empty(
            shape=parzen_est.shape,
            dtype=int
        )

        #print(parzen_est)

        for idx in range(len(classes)):
            if parzen_est[idx, 0] >= parzen_est[idx, 1]:
                classes[idx, 0] = 1
                classes[idx, 1] = 0
            else:
                classes[idx, 0] = 0
                classes[idx, 1] = 0

        return classes[:, 1]

    def predict_probs(self,
                      data: np.ndarray) -> np.ndarray:
        """

        :param data:
        :return:
        """

        parzen_est = self._get_parzen_estimates(data)

        probs = np.empty(
            shape=parzen_est.shape,
            dtype=float
        )

        for idx in range(len(probs)):
            probs[idx, 0] = parzen_est[idx, 0] / (parzen_est[idx, 0] + parzen_est[idx, 1])
            probs[idx, 1] = parzen_est[idx, 1] / (parzen_est[idx, 0] + parzen_est[idx, 1])

        return probs

    def evaluate(self,
                 path_to_dataset: str,
                 save: bool=True):

        """

        :param path_to_dataset:
        :param save:
        :return:
        """

        assert self.config == EvalConfig

        full_df = read_csv(path=path_to_dataset, label_cols=self.config.LABELS)

        results = list()

        for idx in range(1, 11):

            trainX_df, trainY_df, testX_df, testY_df = split_dataframe(
                df=full_df,
                label_cols=self.config.LABELS,
                test_part=idx
            )

            trainX = trainX_df.as_matrix(columns=self.config.FEATURES)
            trainY = trainY_df.as_matrix(columns=self.config.LABELS)

            testX = testX_df.as_matrix(columns=self.config.FEATURES)
            testY = testY_df.as_matrix(columns=self.config.LABELS)

            self.train(
                trainX=trainX,
                trainY=trainY,
                validateX=None,
                validateY=None
            )

            #print(self.weights)
            #print(self.As)

            predY = self.predict_class(testX)

            #print(predY)

            results.append(dict())

            for m in self.config.METRICS:
                results[-1][m] = self.config.METRICS[m](
                    y_true=testY[:, 0],
                    y_pred=predY[:, 0]
                )

            print(results[-1])

        if save:
            path = 'models/evaluation/results/%s' % self.name

            filename = get_new_filename_in_dir(dir_path=path)

            dump_json(data=results, filename=filename)

        return results


