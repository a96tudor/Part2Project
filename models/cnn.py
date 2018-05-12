"""
Part2Project -- cnn.py.py

Copyright Apr 2018 [Tudor Mihai Avram]

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
from keras.models import Sequential

from keras.layers import Reshape
from keras.layers import Flatten
from keras.layers import Conv1D
from keras.layers import Dropout
from keras.layers import Input
from keras.layers import Dense
from keras.optimizers import Adam
from keras.layers import BatchNormalization
from keras.regularizers import L1L2
from keras.callbacks import ModelCheckpoint
import numpy as np

from models.model import Model
from models.config import *


class ConvolutionalNeuralNetwork(Model):
    """
        Class representing the CNN implemented as part of the project
    """

    def __init__(self,
                 config: ModelConfig):
        """
            CONSTRUCTOR

        :param config:      Configuration used when running the model
        """
        super(ConvolutionalNeuralNetwork, self).__init__(config)

        self.model = Sequential()
        self.name = 'cnn'

    def load_checkpoint(self,
                        path: str) -> None:
        """
            Method used to load a pre-trained checkpoint

        :param path:        Path to the checkpoint
        :return:            -
        """
        assert self.config == PredictConfig
        assert self.built

        self.model.load_weights(
            filepath=path
        )

        self.trained = True

    def save_checkpoint(self,
                        path: str) -> None:
        """
            Method not used in this class
        """
        pass

    def setup(self,
              input_dim: tuple,
              **kwargs) -> None:
        """

        :param input_dim:       The shape of the input
        :param kwargs:          Other arguments. Not used here

        :return:                -
        """
        assert not self.built

        model = Sequential()

        model.add(Reshape(
            (1, 23),
            input_shape=(23,)
        ))

        model.add(
            BatchNormalization()
        )

        conv1_layer = Conv1D(
            32,
            kernel_size=2,
            padding='causal',
            # input_shape=(None, len(feature_vector), 1),
            kernel_regularizer=L1L2(l1=.0, l2=.1),
            # activation='elu',
        )

        model.add(conv1_layer)

        # model.add(Dropout(0.2))

        model.add(
            Conv1D(
                64,
                kernel_size=2,
                padding='causal',
                # activation='elu',
                # kernel_regularizer=L1L2(l1=.0, l2=.1)
            )
        )

        # model.add(Dropout(0.2))

        model.add(
            Conv1D(
                128,
                kernel_size=2,
                padding='causal',
                # dilation_rate=4,
                # activation='elu',
                # kernel_regularizer=L1L2(l1=.0, l2=.1)
            )
        )

        model.add(Dropout(
            .2
        ))

        model.add(Flatten())

        model.add(
            Dense(
                128,
                activation='relu',
                # input_dim=len(feature_vector),
                # kernel_regularizer=L1L2(l1=.0, l2=.1)
            )
        )

        model.add(BatchNormalization())

        # model.add(Dropout(0.2))

        model.add(
            Dense(
                32,
                activation='relu',
                # kernel_regularizer=L1L2(l1=.0, l2=.1)
            )
        )

        # model.add(Dropout(0.5))

        model.add(
            Dense(
                2,
                #input_dim=len(feature_vector),
                activation='softmax',
                # kernel_regularizer=L1L2(l1=.0, l2=.1)
            )
        )

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy'
        )

        self.model = model

        self.built = True

    def train(self,
              trainX,
              trainY,
              validateX,
              validateY,
              save_checkpoint: bool = False) -> None:
        """

        :param trainX:                  The training feature vectors
        :param trainY:                  The training labels
        :param validateX:               The validation feature vectors
        :param validateY:               The validation labels
        :param save_checkpoint:         Whether to save the trained checkpoint to disk or not

        :return:                        -
        """
        assert self.built
        assert self.config == EvalConfig or self.config == TrainConfig
        assert self.config == TrainConfig or not save_checkpoint

        if not save_checkpoint:
            self.model.fit(
                x=trainX,
                y=trainY,
                validation_data=(validateX, validateY),
                batch_size=100,
                epochs=1000,
                verbose=0
            )
        else:
            path = self.config.CHECKPOINTS_PATH + "/cnn.hdf5"
            callback = ModelCheckpoint(
                filepath=path,
                save_best_only=True
            )
            self.model.fit(
                x=trainX,
                y=trainY,
                validation_data=(validateX, validateY),
                batch_size=100,
                epochs=1000,
                callbacks=[callback],
                verbose=0
            )

        self.trained = True

    def predict_class(self,
                      data: np.ndarray) -> np.ndarray:
        """

        :param data:   feature matrix for which we do the predictions
        :return:       A numpy ndarray containing the classification results
        """
        assert self.config == PredictConfig or self.config == EvalConfig
        assert self.built
        assert self.trained

        return np.array(
            self.model.predict_classes(
                data,
                batch_size=100,
                verbose=0
            )
        )

    def predict_probs(self,
                      data: np.ndarray):
        """

        :param data:    feature matrix for which we do the predictions
        :return:        A numpy ndarray containing the classification results
        """
        assert self.config == PredictConfig or self.config == EvalConfig
        assert self.built
        assert self.trained

        return np.array(
            self.model.predict_proba(
                data,
                batch_size=100,
                verbose=0
            )
        )
