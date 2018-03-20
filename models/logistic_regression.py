import keras.backend as K
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Optimizer
from keras.regularizers import Regularizer

from models.eval.metrics imprort MCC
from models.config import *

class LogisticRegression(Sequential):
    """
        Class representing Logistic Regression model
    """
    def __init__(self,
                 config):
        """
            CONSTRUCTOR

            :param config:  the configuration of the model
        """
        Sequential.__init__(self)

        self._cnf = config

    def setup(self,
              no_features: int,
              no_labels: int,
              optimiser: Optimizer,
              regulizer: Regularizer = None):
        """

        :param no_features:             # of features in each feature vector
        :param no_labels:               # of possible labels to assign
        :param optimiser:               The class of optimiser we want to use for this model
        :param regulizer:               The Regularizer we wan to use on the input data. default None

        :return:                        -
        """

        self.add(
            Dense(
                no_labels,
                input_shape=no_features,
                kernel_regularizer=regulizer,
                activation='softmax'
            )
        )

        self.compile(
            loss='categorical_crossentropy',
            optimiser=optimiser,
            metrics=['accuracy', MCC],
        )
