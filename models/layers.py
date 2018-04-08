"""
Part2Project -- layers.py

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
from keras import backend as K
from keras import activations, regularizers, constraints, initializers
from keras.layers import Layer, Dropout, LeakyReLU


class GraphAttention(Layer):
    """
        Class implementing the Graph Attention layer, as described by
        Veličković et al in https://arxiv.org/abs/1710.10903.
    """

    def __init__(self,
                 newF:int,
                 attn_dropout:float=.5,
                 activation='relu',
                 kernel_initializer='glorot_uniform',
                 attn_kernel_initializer='glorot_uniform',
                 kernel_regularizer=None,
                 attn_kernel_regularizer=None,
                 kernel_constraint=None,
                 attn_kernel_constraint=None,
                 **kwargs):
        """

        :param newF:                        The output number of features
        :param attn_dropout:                Internal dropout rate for the
                                            attention coefficients. Default 0.5

        :param activation:                  The activation function used by the
                                            layer. Default ReLU (i.e. f(x) = max(0, x) )

        :param kernel_initializer:          Initializer used by the kernel. Default
                                            glorot_uniform. It draws samples from a uniform
                                            distribution within [-l, l], where
                                            l = sqrt(6 / (in + out)). Here in and out are the
                                            number of units in the input and output tensors,
                                            respectively

        :param attn_kernel_initializer:     Initializer used by the attention kernels. Default
                                            glorot_uniform

        :param kernel_regularizer:          Regulizer used by the kernel. Default None.
        :param attn_kernel_regularizer:     Regulizer used by the attention kernel. Default None
        :param kernel_constraint:           Constraints on the kernel. Default None
        :param attn_kernel_constraint:      Constraints on the attention kernel. Default None
        """

        self.newF = newF
        self.attn_dropout = attn_dropout
        self.activation = activations.get(activation)
        self.kernel_initializer = initializers.get(kernel_initializer)
        self.attn_kernel_initializer = initializers.get(attn_kernel_initializer)
        self.kernel_constraint = constraints.get(kernel_constraint)
        self.attn_kernel_constraint = constraints.get(attn_kernel_constraint)
        self.kernel_regularizer = regularizers.get(kernel_regularizer)
        self.attn_kernel_regularizer = regularizers.get(attn_kernel_regularizer)

        self.kernel = None      # Populated in build()
        self.attn_kernel = None  # Populated in build()

        self.output_dim = newF

        self.built = False  # Will be reset by build()

        super(GraphAttention, self).__init__(**kwargs)

    def build(self,
              input_shape):
        """

                Function called when we build the model

        :param input_shape:         The shape of the input to the layer.
                                    Has to be a tuple with length at least 2
        :return:                    -
        """
        assert(len(input_shape)) > 2

        F = input_shape[0][-1]  # Length of input feature vectors

        # LAYER KERNEL - the W matrix in the paper. F x F weights matrix
        self.kernel = self.add_weight(
            shape=(F, self.newF),
            initializer=self.kernel_initializer,
            name='gat_kernel',
            regularizer=self.kernel_regularizer,
            constraint=self.kernel_constraint
        )

        # ATTENTION KERNEL. 2newF x 1 weights matrix
        self_attn_kernel = self.add_weight(
            shape=(self.newF, 1),
            initializer=self.attn_kernel_initializer,
            name='gat_self_attn_kernel',
            regularizer=self.attn_kernel_regularizer,
            constraint=self.attn_kernel_constraint
        )

        neigh_attn_kernel = self.add_weight(
            shape=(self.newF, 1),
            initializer=self.attn_kernel_initializer,
            name='gat_neigh_attn_kernel',
            regularizer=self.attn_kernel_regularizer,
            constraint=self.attn_kernel_constraint
        )

        self.attn_kernel = (self_attn_kernel, neigh_attn_kernel)

        self.built = True

    def call(self,
             inputs,
             **kwargs):
        """

        :param inputs:          GAT layer inputs. Have to be a tuple with the format (X, A)
                                where X = the features matrix (N x F) and A = the adjacency matrix (N x N)

        :return:                The layer output
        """
        X = inputs[0]
        A = inputs[1]

        N = K.shape(X)[0]  # number of nodes in the graph

        outputs = list()

        # Attention network inputs. N x newF matrix
        linear_trans_X = K.dot(X, self.kernel)

        self_attn = K.dot(linear_trans_X, self.attn_kernel[0])
        neigh_attn = K.dot(linear_trans_X, self.attn_kernel[1])

        dense = self_attn + K.transpose(neigh_attn)

        dense = LeakyReLU(alpha=.2)(dense)

        mask = K.switch(
            K.equal(
                A,
                K.constant(0.)
            ),
            K.ones_like(A) * -10e9,
            K.zeros_like(A)
        )

        masked_dense = dense + mask

        # Getting attention coefficients e(i,j)
        softmax = K.softmax(masked_dense)

        dropout = Dropout(rate=self.attn_dropout)(softmax)

        # New feature vectors
        features = K.dot(dropout, linear_trans_X)

        if self.activation is not None:
            features = self.activation(features)

        return features
