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
from keras.activations import relu
import keras.backend as K
from keras.optimizers import Adam
from keras.models import Model
from models.config import *
from keras.regularizers import l2
from models.metrics import *


class GraphAttentionNetwork:
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
        self.config = config
        self.model = None           # To be configured in setup()

    def setup(self,
              features_cnt: int,
              nodes_cnt: int,
              attn_output_lng: int,
              classes_count: int,
              dropout_rate: float):
        """

        :param features_cnt:        # of features for each node
        :param nodes_cnt:           # of nodes taken into consideration
        :param attn_output_lng:     # of features in the output of the attentional layer
        :param classes_count:       # of classes in the output
        :param dropout_rate:        dropout %-ile for the input dropout layer

        :return:                    The keras Model object
        """

        # Defining constants
        l2_reg = 5e-4   # regularization rate for the GraphAttention layer

        # Setting up input layers
        A = Input(shape=(nodes_cnt, ))
        X = Input(shape=(features_cnt, ))

        dropout1 = Dropout(rate=dropout_rate)(X)

        gat_layer = GraphAttention(
            newF=attn_output_lng,
            kernel_regularizer=l2(l2_reg),
            activation='elu'
        )([dropout1, A])

        dropout2 = Dropout(rate=dropout_rate)(gat_layer)

        flatten = Flatten()(dropout2)

        output = Dense(
            units=classes_count,
            activation='softmax'
        )(flatten)

        model = Model(
            inputs=[X, A],
            outputs=output
        )

        model.compile(
            optimizer=Adam(),
            loss='categorical_crossentropy',
            metrics=['acc', MCC]
        )

        return model

