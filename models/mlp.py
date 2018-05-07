"""
Part2Project -- mlp.py

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
from keras.layers import Dropout
from keras.layers import Input
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.layers import BatchNormalization
from keras.regularizers import L1L2
from keras.callbacks import ModelCheckpoint
import numpy as np

from models.model import Model
from models.config import *


class MultilayerPerceptron(Model):
    """
        Class representing a multilayer perceptron.
    """

    def __init__(self,
                 config: ModelConfig):
        """

        :param config:      The configuration the model is being run in
        """

        super(MultilayerPerceptron, self).__init__(config)

        self.model = Sequential()
        self.name = 'mlp'

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
            Method that builds the NN architecture

        :param input_dim:   The dimension of the inputs
        :param kwargs:      Other arguments. Not used here
        :return:            -
        """
        assert not self.built
        # Defining layers
        batchNormLayer1 = BatchNormalization(
            input_shape=input_dim
        )

        dropoutInputLayer = Dropout(
            rate=.2
        )

        denseLayer1 = Dense(
            32,
            activation='relu',
            kernel_regularizer=L1L2(l1=.0, l2=.1),
            kernel_initializer='uniform'
        )

        bathNormLayer2 = BatchNormalization()

        dropoutDenseLayer1 = Dropout(
            rate=.2
        )

        denseLayer2 = Dense(
            16,
            activation='relu',
            kernel_regularizer=L1L2(l1=.0, l2=.1),
            kernel_initializer='uniform'
        )

        bathNormLayer3 = BatchNormalization()

        dropoutDenseLayer2 = Dropout(
            rate=.2
        )

        outputLayer = Dense(
            2,
            activation='softmax',
            kernel_initializer='uniform'
        )

        # adding the layers
        self.model.add(batchNormLayer1)
        self.model.add(dropoutInputLayer)
        self.model.add(denseLayer1)
        self.model.add(bathNormLayer2)
        self.model.add(dropoutDenseLayer1)
        self.model.add(denseLayer2)
        self.model.add(bathNormLayer3)
        self.model.add(dropoutDenseLayer2)
        self.model.add(outputLayer)

        # compiling the model
        self.model.compile(
            optimizer=Adam(),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

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
            path = self.config.CHECKPOINTS_PATH + "/mlp.hdf5"

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
                verbose=0,
                batch_size=100
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
                verbose=0,
                batch_size=100
            )
        )
