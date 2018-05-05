"""
Part2Project -- __init__.py

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
import pandas as pd

AVAILABLE_DATASETS = ['small']
DATASETS_PATH = ['data/datasets']
AVAILABLE_FORMATS = ['csv']


def load_dataset(name:str = None,
                 format:str = None) -> pd.DataFrame:
    """

    :param name:        the name of the dataset.
                        If None, uses 'small' by default. Default None
    :param format:      the format of the dataset.
                        If None, uses '.csv' by default. Default None

    :return:            A pd.Dataframe with all the data from the dataset
    """
