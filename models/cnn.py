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
from keras.layers import Conv1D
from keras.layers import Dropout
from keras.layers import Input
from keras.layers import Dense
from keras.optimizers import Adam
from keras.layers import BatchNormalization
from keras.regularizers import L1L2
from keras.callbacks import ModelCheckpoint
import numpy as np

from models import Model
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

    def load_checkpoint(self,
                        path: str) -> None:
        """
            Method used to load a pre-trained checkpoint

        :param path:        Path to the checkpoint
        :return:            -
        """
        assert isinstance(self.config, PredictConfig)
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

        # Defining the layers
        reshapeLayer = Reshape(
            (1, input_dim[0]),
            input_shape=input_dim
        )

        batchNormLayer1 = BatchNormalization()

        convLayer1 = Conv1D(
            32,
            kernel_size=2,
            padding='casual'
        )

        convLayer2 = Conv1D(
            64,
            kernel_size=2,
            padding='casual'
        )

        convLayer3 = Conv1D(
            128,
            kernel_size=2,
            padding='casual'
        )

        dropoutLayer = Dropout(
            0.2
        )

        denseLayer = Dense(
            32,
            kernel_initializer='uniform',
            kernel_regularizer=L1L2(l1=.0, l2=.1),
            activation='relu'
        )

        batchNormLayer2 = BatchNormalization()

        outputLayer = Dense(
            2,
            activation='softmax',
            kernel_initializer='uniform'
        )

        # Adding them to the model
        self.model.add(reshapeLayer)
        self.model.add(batchNormLayer1)
        self.model.add(convLayer1)
        self.model.add(convLayer2)
        self.model.add(convLayer3)
        self.model.add(dropoutLayer)
        self.model.add(denseLayer)
        self.model.add(batchNormLayer2)
        self.model.add(outputLayer)

        # Compiling the model
        self.model.compile(
            optimizer=Adam(),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

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
        assert isinstance(self.config, (EvalConfig, TrainConfig, ))
        assert isinstance(self.config, TrainConfig) or not save_checkpoint

        if not save_checkpoint:
            self.model.fit(
                x=trainX,
                y=trainY,
                validation_data=(validateX, validateY),
                batch_size=100,
                epochs=1000
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
                callbacks=[callback]
            )

        self.trained = True

    def predict_class(self,
                      data: np.ndarray) -> np.ndarray:
        """

        :param data:   feature matrix for which we do the predictions
        :return:       A numpy ndarray containing the classification results
        """
        assert isinstance(self.config, (PredictConfig, EvalConfig, ))
        assert self.built
        assert self.trained

        return np.array(
            self.model.predict(
                data,
                batch_size=100,
                steps=100,
                verbose=0
            )
        )

    def predict_probs(self,
                      data: np.ndarray):
        """

        :param data:    feature matrix for which we do the predictions
        :return:        A numpy ndarray containing the classification results
        """
        assert isinstance(self.config, (PredictConfig, EvalConfig, ))
        assert self.built
        assert self.trained

        return np.array(
            self.model.predict_proba(
                data,
                batch_size=100,
                steps=100,
                verbose=0
            )
        )

