import tensorflow as tf
import pandas as pd
import numpy as np

_UNWANTED_COLUMNS = [
    "UUID",
    "TIMESTAMP",
    "LABEL"
]

_Y_COL = "LABEL"

_SHAPE = []

class LogisticRegression:

    def __init__(self, train_path, test_path, log=False):
        """
                CONSTRUCTOR

        :param train_path:      path to the training set
        :param test_path:       path to the test set
        :param log:             whether I want to print logs to the console or not
        """
        self._train_path = train_path
        self._test_path = test_path
        self._log = log

        # SETTING UP PARAMETERS
        if log:
            print("Initialising parameters...")

        self._learning_rate = 0.01
        self._training_epochs = 25
        self._batch_size = 1000
        self._display_step = 1

        if log:
            print("=================================")
            print("Done! The parameters are: ")
            print("Learning rate: ", self._learning_rate)
            print("Training epochs: ", self._training_epochs)
            print("Batch size: ", self._batch_size)
            print("=================================")

        # INITIALISING TF FUNCTIONS TO None

    def setup(self):
        """
                Method that does the setup for the model. It:
                        - reads the training data from the given file
                        - sets up tensorflow functions
        :return:
        """
        #  READING DATA

        if self._log:
            print("Reading data...")

        train = pd.read_csv(self._train_path)
        Ys = train.as_matrix(columns=[_Y_COL])

        train.drop(columns=_UNWANTED_COLUMNS)
        Xs = train.as_matrix()

        data_cnt = train.shape[0]  # number of rows in the dataframe
        dim = train.shape[1]       # number of dimensions
        nclass = 2                 # number of classes

        if self._log:
            print("Done!")
            print("%d train examples loaded" % data_cnt)
            print("%d dimensions" % dim)
            print("%d classes" % nclass)

        # SETTING UP TENSORFLOW VARIABLES
        if self._log:
            print("Setting up weights tensors")

        w_tensor = tf.Variable(tf.zeros())
        b_tensor = tf.Variable(tf.zeros(2))

        if self._log:
            print("Setting up TensorFlow Graph input")

        x = tf.placeholder('float', [None, dim])
        y = tf.placeholder('float', [None, nclass])

        # SETTING UP FUNCTIONS
        if self._log:
            print("Setting up TensorFlow functions")

        WEIGHT_DECAY_FACTOR = 1  # 10^(-6)

        l2_loss = tf.add_n(
            tf.nn.l2_loss(v) for v in tf.trainable_variables()
        )

        _pred = tf.nn.softmax(tf.matmul(x, w_tensor) + b_tensor)
        cost = tf.reduce_mean(
            -tf.reduce_sum(y * tf.log(_pred)),
            reduction_indices=1
        )
        self._cost = cost + WEIGHT_DECAY_FACTOR*l2_loss

        optm = tf.train.GradientDescentOptimizer(self._learning_rate).minimize(cost)

        _corr = tf.equal(
            tf.argmax(_pred, 1),
            tf.argmax(y, 1)
        )
        self._accr = tf.reduce_mean(
            tf.cast(_corr, tf.float32)
        )

        self_init = tf.initialize_all_variables()

        if self._log:
            print("DONE! Setup successful!")

    