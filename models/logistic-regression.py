import tensorflow as tf
import pandas as pd

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
        self._batch_size = 100
        self._display_step = 1

        if log:
            print("=================================")
            print("Done! The parameters are: ")
            print("Learning rate: ", self._learning_rate)
            print("Training epochs: ", self._training_epochs)
            print("Batch size: ", self._batch_size)
            print("=================================")
            

