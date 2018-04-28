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
                 self_importance=.25,
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
        :param self_importance:             How much importance to accord to the input feature
                                            vector. Default 0.25
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

        self.self_importance = self_importance

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

        # LAYER KERNEL - the W matrix in the paper. F x newF weights matrix
        self.kernel = self.add_weight(
            shape=(F, self.newF),
            initializer=self.kernel_initializer,
            name='gat_kernel',
            regularizer=self.kernel_regularizer,
            constraint=self.kernel_constraint
        )

        # ATTENTION KERNEL. 2newF x 1 weights vector
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

        :param inputs:          GAT layer inputs. Have to be a tuple with the format (x, X)
                                where:  x = feature vector for the node
                                        X = feature matrix for the neighbours of the node

        :return:                The layer output
        """
        x = inputs[0]       # Feature vector of the input node
        X = inputs[1]       # Feature vectors of the neighbours

        N = K.shape(X)[0]

        features = None

        # Linear transformations for both x and X

        x_transformed = K.dot(x, self.kernel)   # (1 x F) * (F x F') = (1 x F')
        X_transformed = K.dot(X, self.kernel)   # (n x F) * (F x F') = (n x F')

        # Now computing a^T(Wh_i||Wh_j) for every neighbour h_j
        # Note: I am using the fact that [a_1||a_2]^T(Wh_i||Wh_j) = a_1^T * Wh_i + a_2^T * Wh_j
        attn_for_self = K.dot(x_transformed, self.attn_kernel[0])   # (1 x F') * (F' x 1) = (1 x 1)
        attn_for_neighs = K.dot(X_transformed, self.attn_kernel[1])  # (n x F') * (F' x 1) = (n x 1)

        # Repeating a_1^T * Wh_i n times
        attn_for_self_repeat = K.repeat_elements(attn_for_self, rep=N, axis=0)

        # Adding them up, to get a^T(Wh_i||Wh_j)
        dense = attn_for_self_repeat + attn_for_neighs  # (n x 1) + (n x 1) = (n x 1)
        dense = K.transpose(dense)  # (n x 1)^T  = (1 x n)

        # Masking the values before activation
        mask = K.ones(shape=(1, N, ))
        mask = K.exp(mask * -10e9) * -10e9

        masked = dense + mask

        # Computing alpha_i,j = softmax(a^T[Wh_i||Wh_j])
        softmax = K.softmax(masked)

        # Adding dropout
        dropout = Dropout(self.attn_dropout)(softmax)

        # Calculating the feature vector with respect with the neighbours
        # neigh = dropout^T * X_transformed
        features_neigh = K.dot(dropout, X_transformed)  # (1 x n) * (n x F') = (1 x F')

        # Now, the final step
        # newH_i = (1-self_importance)*neigh + self_imporance *x_transformed
        features = (1-self.self_importance) * features_neigh + self.self_importance * x_transformed

        return features
