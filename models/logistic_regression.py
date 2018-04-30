import keras.backend as K
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import SGD
from keras.layers import BatchNormalization
from keras.regularizers import L1L2
from keras.callbacks import ModelCheckpoint
import numpy as np

from models import Model
from models.config import *


class LogisticRegression(Model):
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
        super(LogisticRegression, self).__init__(config)

        self.model = Sequential()

    def load_checkpoint(self,
                        path: str) -> None:
        """

        :param path:        Path to load the checkpoint from
        :return:            -
        """
        assert self.built

        self.model.load_weights(
            filepath=path
        )

    def save_checkpoint(self,
                        path: str) -> None:
        """
            Not used in this case.
            The checkpoint saving is done using a callback while training.
        """
        pass

    def setup(self,
              input_dim: tuple,
              **kwargs) -> None:
        """
            Method used to setup the Keras machine learning model

        :param input_dim:        Dimensions of the input vectors
        :param kwargs:           Other potential arguments. Not applicable here.
        :return:                 -
        """

        # Defining layers
        batchNormLayer = BatchNormalization(
            input_shape=input_dim
        )

        denseLayer = Dense(
            2,
            activation='softmax',
            kernel_regularizer=L1L2(l1=.0, l2=.1),
            kernel_initializer='uniform'
        )

        # Adding layers
        self.model.add(batchNormLayer)
        self.model.add(denseLayer)

        # Compiling model

        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=SGD(lr=0.001),
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
                Method used to train the model

        :param trainX:              np.ndarray containing the training set feature vectors
        :param trainY:              np.ndarray containing the training set labels
        :param validateX:           np.ndarray containing the validation set feature vectors
        :param validateY:           np.ndarray containing the validation set labels
        :param save_checkpoint:     Whether to save the model checkpoint or not

        :return:                    -
        """

        assert isinstance(self.config, (TrainConfig, EvalConfig, ))
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
            # We want to save the checkpoints.
            # Thus, adding a callback that handles that as well
            path = self.config.CHECKPOINTS_PATH + "/logistic_regression.hdf5"
            checkpointer = ModelCheckpoint(
                filepath=path,
                save_best_only=True
            )
            self.model.fit(
                x=trainX,
                y=trainY,
                validation_data=(validateX, validateY),
                batch_size=100,
                epochs=1000
            )

    def predict_class(self,
                      data: np.ndarray) -> np.ndarray:
        """

        :param data:   feature matrix for which we do the predictions
        :return:       A numpy ndarray containing the classification results
        """

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

        return np.array(
            self.model.predict_proba(
                data,
                batch_size=100,
                steps=100,
                verbose=0
            )
        )
