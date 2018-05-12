"""
Part2Project -- gat.py.py

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

from models.layers import GraphAttention
from keras.layers import Input, Dense, Dropout, Flatten
from keras.optimizers import Adam
from keras.models import Model
from models.config import *
from keras.regularizers import l2
from keras.regularizers import L1L2
from keras.layers import BatchNormalization
from keras.callbacks import ModelCheckpoint

from models.evaluation.metrics import *
from models import model
from data.utils import load_json, split_list, process_list


class GraphAttentionNetwork(model.Model):
    """
        Class representing a Graph Attention Network
    """

    def __init__(self,
                 config: ModelConfig,
                 **kwargs):
        """
                CONSTRUCTOR

        :param config:      The configuration used by the model in question
        """
        super(GraphAttentionNetwork, self).__init__(config)

        self.model = None           # To be configured in setup()
        self.name = 'gat'

    def setup(self,
              input_dim: tuple,
              **kwargs) -> None:
        """
            Method used to setup the model's components

        :param input_dim:
        :param kwargs:
        :return:
        """

        assert not self.built

        F = len(self.config.FEATURES)
        newF = 32                   # The new feature dimension
        lr = 5e-3

        X_in = Input(
            shape=(F, )             # The input for the feature matrix
        )

        N_in = Input(
            shape=(20, F, )       # The input for the neighbourhood data
        )

        inputDropoutLayer = Dropout(
            rate=.6
        )(X_in)

        attentionalLayer = GraphAttention(
            newF=newF,
            activation='elu',
            kernel_regularizer=l2(5e-4)
        )([inputDropoutLayer, N_in])

        attentionDropout = Dropout(
            rate=.6
        )(attentionalLayer)

        denseLayer = Dense(
            16,
            activation='relu',
            kernel_regularizer=L1L2(l1=.0, l2=.1),
            kernel_initializer='uniform'
        )(attentionDropout)

        denseBatchNorm = BatchNormalization()(denseLayer)

        outputLayer = Dense(
            2,
            activation='softmax',
            kernel_initializer='uniform',
            kernel_regularizer=L1L2(l1=.0, l2=.1)
        )(denseBatchNorm)

        self.model = Model(
            inputs=[X_in, N_in],
            outputs=outputLayer
        )

        optimiser = Adam(lr=lr)

        self.model.compile(
            optimizer=optimiser,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        self.built = True

    def train(self,
              trainX,
              trainY,
              validateX,
              validateY,
              save_checkpoint: bool = False):
        """

        :param trainX:              The train input. Needs to be in the format:
                                        [X, N], where:
                                            - X = the feature matrix for all the nodes. shape = (23, )
                                            - N = the neighbourhood data for all nodes. shape = (23, None, )

        :param trainY:              The train output. Needs to be in the a (2, ) np.ndarray with
                                    one-hot-encoding of the two classes

        :param validateX:           The validation input. Needs to be in the format:
                                        [X, N], where:
                                            - X = the feature matrix for all the nodes. shape = (23, )
                                            - N = the neighbourhood data for all nodes. shape = (23, None, )

        :param validateY:           The validation output. Needs to be in the a (2, ) np.ndarray with
                                    one-hot-encoding of the two classes

        :param save_checkpoint:     Whether to save the checkpoint after training or not

        :return:                    -
        """
        assert self.config in [EvalConfig, TrainConfig]
        assert self.built

        if not save_checkpoint:
            self.model.fit(
                x=trainX,
                y=trainY,
                validation_data=(validateX, validateY),
                epochs=2000,
                batch_size=100
            )
        else:
            path = self.config.CHECKPOINTS_PATH + "/gat.hdf5"

            callback = ModelCheckpoint(
                filepath=path,
                save_best_only=True
            )

            self.model.fit(
                x=trainX,
                y=trainY,
                validation_data=(validateX, validateY),
                epochs=2000,
                batch_size=100,
                callbacks=[callback]
            )

    def predict_class(self,
                      data: list) -> np.ndarray:
        """

        :param data:
        :return:
        """

        assert self.config == EvalConfig or self.config == PredictConfig

        SHOW_probs = self.model.predict(
            data,
            batch_size=min(100, len(data[0])),
            verbose=0
        )

        return np.array([
            1 if prob >= .5 else 0
            for prob in SHOW_probs
        ])

    def predict_probs(self,
                      data: np.ndarray):

        """

        :param data:
        :return:
        """

        assert self.config == EvalConfig or self.config == PredictConfig

        SHOW_probs = self.model.predict()

        result = np.empty(
            shape=(len(data), 2)
        )

        result[:, 0] = SHOW_probs
        result[:, 1] = 1.0 - SHOW_probs

        return result

    def load_checkpoint(self,
                        path: str):
        """

        :param path:
        :return:
        """

        assert self.config == PredictConfig

        self.model.load_weights()

    def save_checkpoint(self,
                        path: str):
        """
            Not used here
        :param path:
        :return:
        """
        pass

    def evaluate(self,
                 path_to_dataset: str,
                 save: bool=True):
        """

        :param path_to_dataset:
        :param save:
        :return:
        """

        assert self.config == EvalConfig

        full_list = load_json(path=path_to_dataset)
        results = list()

        for idx in range(1, 11):

            train_list, test_list = split_list(
                data=full_list,
                test_section=idx
            )

            train_list, validate_list = split_list(
                data=train_list,
                test_section=1,
                purpose='validation'
            )

            trainX, trainN, trainY = process_list(
                data=train_list,
                labels=self.config.LABELS,
                features=self.config.FEATURES
            )

            testX, testN, testY = process_list(
                data=test_list,
                labels=self.config.LABELS,
                features=self.config.FEATURES
            )

            validX, validN, validY = process_list(
                data=validate_list,
                labels=self.config.LABELS,
                features=self.config.FEATURES
            )

            self.train(
                trainX=[trainX, trainN],
                trainY=trainY,
                validateX=[validX, validN],
                validateY=validY
            )

            predY = self.predict_class(
                data=[testX, testN]
            )

            results.append(dict())

            for m in self.config.METRICS:
                results[-1][m] = self.config.METRICS[m](
                    y_pred=predY,
                    y_true=testY[:, 1]
                )

            print(results[-1])

        return results