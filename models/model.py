"""
Part2Project -- model.py

Copyright May 2018 [Tudor Mihai Avram]

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
from data.utils import read_csv, split_dataframe, get_new_filename_in_dir, dump_json
from models.config import *

import numpy as np
import pandas as pd
import abc


class Model(object):
    """
        ABSTRACT base class for the ML models implemented
    """

    def __init__(self,
                 config: ModelConfig):
        """
            CONSTRUCTOR

        :param config:      The configuration used when running the model
        """
        self.config = config
        self.built = False
        self.trained = False
        self.name = 'model'

    @abc.abstractclassmethod
    def load_checkpoint(self,
                        path: str) -> None:
        pass

    @abc.abstractclassmethod
    def save_checkpoint(self,
                        path: str) -> None:
        pass

    @abc.abstractclassmethod
    def setup(self,
              input_dim: tuple,
              **kwargs) -> None:

        pass

    @abc.abstractclassmethod
    def train(self,
              trainX,
              trainY,
              validateX,
              validateY,
              save_checkpoint: bool = False) -> None:

        pass

    @abc.abstractclassmethod
    def predict_class(self,
                      data: np.ndarray) -> np.ndarray:

        pass

    @abc.abstractclassmethod
    def predict_probs(self,
                      data: np.ndarray) -> np.ndarray:

        pass

    def evaluate(self,
                 path_to_dataset: str,
                 save: bool=True) -> dict:
        """

            Method that evaluates the model using the K-fold Cross Validation
            technique.

        :param path_to_dataset:     The path to the dataset we're loading for evaluation
        :return:                    The resulting metrics
        """
        assert(self.config == EvalConfig)

        dataset = read_csv(
            path=path_to_dataset,
            label_cols=self.config.LABELS
        )

        results = dict()

        for test_section in range(1, 11):

            Xs, Ys, testXs_df, testYs_df = split_dataframe(
                df=dataset,
                test_part=test_section,
                label_cols=self.config.LABELS
            )

            testXs = testXs_df.as_matrix(columns=self.config.FEATURES)
            testYs = testYs_df.as_matrix(columns=self.config.LABELS)

            full_train = pd.concat([Xs, Ys], axis=1)

            for validation_section in range(1, 11):

                trainXs_df, trainYs_df, validXs_df, validYs_df = split_dataframe(
                    df=full_train,
                    test_part=validation_section,
                    label_cols=self.config.LABELS
                )

                trainXs = trainXs_df.as_matrix(columns=self.config.FEATURES)
                trainYs = trainYs_df.as_matrix(columns=self.config.LABELS)
                validXs = validXs_df.as_matrix(columns=self.config.FEATURES)
                validYs = validYs_df.as_matrix(columns=self.config.LABELS)

                self.train(
                    trainX=trainXs,
                    trainY=trainYs,
                    validateX=validXs,
                    validateY=validYs
                )

                predict_Ys = self.predict_class(testXs)

                results[(test_section, validation_section, )] = dict()

                for m in self.config.METRICS:
                    results[(test_section, validation_section, )][m] = self.config.METRICS[m](
                        y_pred=predict_Ys,
                        y_true=testYs[:, 1]
                    )
                print(results[(test_section, validation_section, )])

        if save:
            dir_name = 'models/evaluation/results/%s' % self.name
            file_path = get_new_filename_in_dir(
                dir_path=dir_name
            )
            dump_json(
                data=results,
                filename=file_path
            )

        return results

