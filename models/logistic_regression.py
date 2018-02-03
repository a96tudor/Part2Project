import tensorflow as tf
import pandas as pd
import numpy as np

_UNWANTED_COLUMNS = [
    "UUID",
    "TIMESTAMP",
    "LABEL"
]

_Y_COL = "LABEL"

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
        self._Ys = train.as_matrix(columns=[_Y_COL])

        train.drop(columns=_UNWANTED_COLUMNS)
        self._Xs = train.as_matrix()

        self._data_cnt = train.shape[0]  # number of rows in the dataframe
        self._dim = train.shape[1]       # number of dimensions
        self._nclass = 2                 # number of classes

        if self._log:
            print("=================================")
            print("Done reading data!")
            print("%d train examples loaded" % self._data_cnt)
            print("%d dimensions" % self._dim)
            print("%d classes" % self._nclass)
            print("=================================")

        # SETTING UP TENSORFLOW VARIABLES
        if self._log:
            print("Setting up weights tensors")

        w_tensor = tf.Variable(tf.zeros([self._dim, self._nclass]), name='weights')
        b_tensor = tf.Variable(tf.zeros([self._nclass]))

        if self._log:
            print("Setting up TensorFlow Graph input")

        self._x = tf.placeholder('float', [None, self._dim])
        self._y = tf.placeholder('float', [None, self._nclass])

        # SETTING UP FUNCTIONS
        if self._log:
            print("Setting up TensorFlow functions")

        WEIGHT_DECAY_FACTOR = 1  # 10^(-6)

        l2_loss = tf.add_n(
            tf.nn.l2_loss(v) for v in tf.trainable_variables()
        )

        _pred = tf.nn.softmax(tf.matmul(self._x, w_tensor) + b_tensor)
        cost = tf.reduce_mean(
            -tf.reduce_sum(y * tf.log(_pred)),
            reduction_indices=1
        )
        self._cost = cost + WEIGHT_DECAY_FACTOR*l2_loss

        self._optm = tf.train.GradientDescentOptimizer(self._learning_rate).minimize(cost)

        _corr = tf.equal(
            tf.argmax(_pred, 1),
            tf.argmax(y, 1)
        )
        self._accr = tf.reduce_mean(
            tf.cast(_corr, tf.float32)
        )

        self._init = tf.initialize_all_variables()

        if self._log:
            print("DONE! Setup successful!")

    def optimise(self):
        """
            Optimising the model!

        :return: -
        """

        with tf.Session() as sess:
            for epoch in range(self._training_epochs):
                sess.run(self._init)
                avg_cost = 0
                num_batch = int(self._data_cnt / self._batch_size)

                for i in range(num_batch):
                    randidx = np.random.randint(self._data_cnt, size=self._batch_size)

                    batch_Xs = self.Xs[randidx, :]
                    batch_Ys = self._Ys[randidx, :]

                    # Fitting using the data in the current batch
                    sess.run(
                        self._optm,
                        feed_dict={
                            self._x: batch_Xs,
                            self._y: batch_Ys
                        }
                    )

                    # Computing average loss
                    avg_cost += sess.run(
                        self._cost,
                        feed_dict={
                            self._x: batch_Xs,
                            self._Ys: batch_Ys
                        }
                    ) / num_batch

                if self._log and epoch % self._display_step == 0:
                    print("=================================")

                    print("Epoch %03d/%03d cost: %.9f" % (epoch, self._training_epochs, avg_cost))

                    train_acc = sess.run(
                                    self._accr,
                                    feed_dict={
                                        self._x: self._Xs,
                                        self._y: self._Ys
                                    }
                                )
                    print("Training accuracy: %.4f" % train_acc)




