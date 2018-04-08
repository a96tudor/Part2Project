"""
Part2Project -- 2-layer-neural-net.py

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
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Optimizer
from keras.regularizers import Regularizer

from models.evaluation.metrics import mcc
from models.config import *


class TwoLayerNeuralNetwork(Sequential):
    """
        Class representing Logistic Regression model
    """
    def __init__(self,
                 config: ModelConfig,
                 **kwargs):
        """
            CONSTRUCTOR

            :param config:  the configuration of the model
        """
        super(TwoLayerNeuralNetwork, self).__init__(**kwargs)

        self._cnf = config

    def setup(self,
              no_features: int,
              no_labels: int,
              optimiser: Optimizer,
              regularizer: Regularizer = None):
        """

        :param no_features:             # of features in each feature vector
        :param no_labels:               # of labels we want to return
        :param optimiser:               Optimizer used by the the model
        :param regularizer:             Regularizer used on the input data. Default None.
        :return:
        """

        self.add(
            Dense(
                2 * no_features,
                input_shape=no_features,
                kernel_regularizer=regularizer,
                activation='relu'
            )
        )

        self.add(
            Dense(
                no_labels,
                activation='softmax'
            )
        )

        self.compile(
            loss='categorical_crossentropy',
            optimiser=optimiser,
            metrics=['accuracy', mcc],
        )
