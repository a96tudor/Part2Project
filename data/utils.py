"""
Part2Project -- utils.py

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
import numpy as np
from sklearn.utils import shuffle
import random
import json
import os


def get_features_and_labels(df, label_cols):
    """
        Function that splits a given dataframe into features and labels

    :param df:              The dataframe we want to split
    :param label_cols:      List of columns that specify labels
    :return:                X = the features matrix
                            Y = the labels vector
    """

    feature_cols = get_diff(df.columns.values, label_cols)

    return df.loc[:, feature_cols], df.loc[:, label_cols]


def get_diff(l1, l2):
    """
        Function that computes the difference between two lists

    :param l1:       The list we want to substract from
    :param l2:       The list we want to substract
    :return:         The resulting list
    """
    return list(set(l1) - set(l2))


def read_csv(path, label_cols, drop_cols=None, normalize=True, shuffle=True):
    """

    :param path:            The path where we want to read the data from
    :param label_cols:      List of columns that specify labels
    :param drop_cols:       List of columns to be dropped from the read data. Default None
    :param normalize:       If we want the data we read to be normalized, by column. See normalize() for more detail.
                                Default True
    :return:                The dataframe we read
    """

    df = pd.read_csv(path)

    if shuffle:
        df = shuffle_df(df)

    if drop_cols is not None:
        df = df.drop(columns=drop_cols)

    if normalize:
        feature_cols = get_diff(df.columns.values, label_cols)
        df.loc[:, feature_cols] = normalize_df(df.loc[:, feature_cols])

    # print(df.head)

    return df


def read_data_from_csv(file, label_cols, drop_cols=None, split=True, normalize=True, shuffle=True):
    """
    :param file:            Path to the csv file where to read the data from
    :param drop_cols:       List of columns to be dropped from the read data. Default None
    :param label_cols:      List of columns that specify labels
    :param split:           If we also want to split the data into training/testing set or not. Default True
    :param normalize:       If we want the data we read to be normalized, by column. See normalize() for more detail.
                                Default True
    :param shuffle:         If we want the dataframe to be shuffled, as well. Default True
    :return:                The data, either as an np.ndarray or as a pd.DataFrame
                            By 'the data', I mean a pair (X, Y) where X are the features and Y are the labels
    """

    df = pd.read_csv(file)

    print(df.iloc[0, :].loc['HIDE'])

    if shuffle:
        df = shuffle_df(df)

    if drop_cols is not None:
        df = df.drop(columns=drop_cols)

    if normalize:
        df1 = df.loc[:, label_cols]
        df2 = normalize_df(df.loc[:, list(set(df.columns.values) - set(label_cols))])
        df = pd.concat([df1, df2], axis=1)

    if split:
        return split_dataframe(df, test_part=1, label_cols=label_cols)

    df_Ys = df.loc[:, label_cols]

    df_Xs = df.loc[:, list(set(df.columns.values) - set(label_cols))]

    return df_Xs, df_Ys


def random_split_dataframe(df, label_cols, percentile=.75):
    """
    :param df:              the dataframe we want to split
    :label_cols:            column names that represent labels (i.e. the Ys in the output)
    :param percentile:      the % of the ndarray that will still be in the 1st part. Default .75
    :return:                4 dataframes, representing:
                                1. 1st part features
                                2. 1st part labels
                                3. 2nd part features
                                4. 2nd part labels
    """

    rows_cnt = len(df)
    rows_cnt_1st = int(rows_cnt * percentile)
    rows_cnt_2nd = int(rows_cnt - rows_cnt_1st)

    X_cols = list(set(df.columns.values) - set(label_cols))
    Y_cols = label_cols

    # GETTING RANDOM INDEXES FOR 1st part
    idx_1st = np.random.choice(rows_cnt, size=rows_cnt_1st, replace=False)
    idx_2nd = list(set(range(rows_cnt)) - set(idx_1st))

    df_1st_Xs = df.loc[idx_1st, X_cols]
    df_1st_Ys = df.loc[idx_1st, Y_cols]
    df_2nd_Xs = df.loc[idx_2nd, X_cols]
    df_2nd_Ys = df.loc[idx_2nd, Y_cols]

    if list(set(df_1st_Xs.index.values).intersection(set(df_2nd_Xs.index.values))) != []:
        print("ERROR: NOT DISJOINT!")

    return df_1st_Xs, df_1st_Ys, \
           df_2nd_Xs, df_2nd_Ys


def normalize_df(df):
    """
    :param df:      The dataframe we want to normalize
    :return:        The normalized dataframe
    """

    # TODO: IMPLEMENT THIS
    return df


def split_dataframe(df, label_cols, test_part, percentile=0.90):
    """
    :param df:                  The DataFrame we want to split
    :param label_cols:          The names of the columns that represent  the labels
    :param test_part:           The test_part^th (1-percentile) section of the df will be used as the test set
    :param percentile:          What percent of the entries is in the training set
    :return:                    4 dataframes, representing:
                                    1. training features
                                    2. training labels
                                    3. test features
                                    4. test labels
    """
    print()
    print("Starting new split: \n    Dataframe length: %d \n    Test section: %d" % (len(df), test_part))
    test_left = int((1 - percentile) * (test_part - 1) * len(df))
    test_right = min(int((1 - percentile) * test_part * len(df) - 1), len(df) - 1)

    print("Test interval: %d - %d" % (test_left, test_right))
    print()

    testDF = df.iloc[test_left:test_right, :]

    if test_left == 0:
        trainDF = df.iloc[test_right + 1:, :]
    elif test_right == len(df) - 1:
        trainDF = df.iloc[:test_left - 1, :]
    else:
        df1 = df.iloc[:test_left - 1, :]
        df2 = df.iloc[test_right + 1, :]

        df2 = df.iloc[test_right + 1:, :]
        trainDF = pd.concat([df1, df2], axis=0, ignore_index=True)

    trainX, trainY = get_features_and_labels(trainDF, label_cols)
    testX, testY = get_features_and_labels(testDF, label_cols)

    return trainX, trainY, testX, testY


def shuffle_df(df):
    """
        Functions that takes a path to a csv, shuffles and returns the content as a
    :param df:                  Dataframe we want to shuffle
    :return:                    -
    """
    return shuffle(df).reset_index(drop=True)


def print_dict(data):
    """

    :param data:       The dictionary we want to print
    :return:
    """
    for key in data:
        print("%s: %.5f" % (str(key), float(data[key])))


def shuffle_dict(data: dict) -> dict:
    """
        Method that shuffles a given dictionary

    :param data:        The dictionary we want to shuffle
    :return:            The shuffled dict
    """

    keys = list(data.keys())
    result = dict()

    random.shuffle(keys)

    for key in keys:
        result[key] = data[key]

    return result


def shuffle_list(data: list) -> list:
    """
        Method that shuffles a given list

    :param data:        The list to shuffle
    :return:            THe shuffled list
    """
    keys = list(range(len(data)))
    random.shuffle(keys)
    result = list()

    for key in keys:
        result.append(data[key])

    return result


def dump_json(data,
              filename):
    """
        Method that saves a dictionary/ list to a JSON file on disk.

    :param data:            the data we want to save. Has to be either a list or a dictionary
    :param filename:        full path to the file we're saving it to

    :return:                -
    """
    try:
        assert (type(data) in [list, dict])
    except AssertionError:
        print("Invalid datatype! Expected list or dict, got ", type(data))
        return

    with open(filename, 'w') as fout:
        json.dump(data, fout)


def intersect_two_lists(l1: list,
                        l2: list) -> list:
    """
        Method used to intersect two given lists

    :param l1:          The first list
    :param l2:          The second list
    :return:            Their intersection, as a new list
    """
    result = list()

    for x in l1:
        if x in l2:
            result.append(x)

    return result


def get_new_filename_in_dir(dir_path: str,
                            format: str = 'json') -> str:
    """

    :param dir_path:    The directory were we're looking in
    :param format:      The format we want the file to be in
    :return:            The full path to the new file
    """

    existent_docs = [
        {
            'name': x.split('.')[0],
            'format': x.split('.')[1]
        } if len(x.split('.')) == 2 else None for x in os.listdir(dir_path)
    ]

    next_idx = 1

    if len(existent_docs) > 0:
        next_idx = max([
            int(x['name']) if x and x['format'] == format else 0
            for x in existent_docs
        ]) + 1

    file_path = "%s/%d.%s" % (dir_path, next_idx, format)

    return file_path


def split_list(data: list,
               test_section: int,
               percentile: float = .90,
               purpose: str = 'test') -> (list, list):
    """
        Function for splitting a list, used in the
        evauation phase of the machine learning models

    :param data:            The initial list to split
    :param test_section:    Which section of the list will act as the test/ validation part
    :param percentile:      How many of the elements are in the training set
    :param purpose:         If it's for validation or testing. Default 'test'

    :return:                The 2 lists resulting from the splitting
    """

    assert purpose in ['test', 'validation']
    assert test_section <= int(1.0 / (1 - percentile))

    test_left = int((1 - percentile) * (test_section - 1) * len(data))
    test_right = min(int((1 - percentile) * test_section * len(data) - 1), len(data) - 1)

    print()
    print("Starting new split:")
    print("   list length: %d" % len(data))
    print("   %s section: %d" % (purpose, test_section))
    print("   %s interval: %d - %d" % (purpose, test_left, test_right))
    print()

    test_list = data[test_left + 1:test_right + 2]
    train_list = data[:test_left + 1] + data[test_right + 2:]

    return train_list, test_list


def append_dict_to_df(new_data: dict,
                      df: pd.DataFrame) -> pd.DataFrame:
    """
        Method that takes a dictionary and appends it
        as a new line to a dataframe

    :param new_data:        The dictionary to append
    :param df:              The dataframe to append to
    :return:                The resulting dataframe
    """

    new_df = pd.DataFrame(
        new_data,
        index=[0]
    )

    result = pd.concat([df, new_df], axis=0, ignore_index=True)

    return result


def process_list(data: list,
                 labels: list,
                 features: list) -> (tuple, np.ndarray):
    """
        Function that gets a list in the format for GAT
        and returns:

                1. A tuple containing two elements (X, N), where:
                    a) X = the feature matrix for the nodes in the list
                         - np.ndarray with shape (len(data), 23)

                    b) N = 3D np.ndarray, with dimension: (len(data), None, 23)
                        it contains the neighbourhood data for the input vectors

                2. An np.ndaray having shape (len(data), 2). It represents the
                labels of the feature vectors

    :param data:            The input list of nodes, with their features
    :param labels:          The label names used when building the np.ndarray
    :param features:        The feature names used when building the feature
                            matrices

    :return:                Listed above
    """

    assert len(data) > 0

    X_df = pd.DataFrame(
        columns=features
    )

    Y_df = pd.DataFrame(
        columns=labels
    )

    N_list = list()

    print("Starting to process the list. %d nodes to process." % len(data))

    cnt_done = 0

    N = np.zeros(
        shape=(len(data), 20, len(features))
    )

    for idx in range(len(data)):
        # Adding node to feature matrix
        node = data[idx]
        self = node['self']
        X_df = append_dict_to_df(new_data=self, df=X_df)

        # Now moving onto neighbours
        neighs_df = pd.DataFrame(
            columns=features
        )
        try:
            for neigh in node['neighs'][:20]:
                neighs_df = append_dict_to_df(new_data=neigh, df=neighs_df)
        except KeyError:
            print(node)

        N_list.append(
            neighs_df.as_matrix(columns=features)
        )

        N[idx, :len(neighs_df), :] = neighs_df.as_matrix(columns=features)

        # And now the labels
        Y_df = append_dict_to_df(
            new_data={
                'SHOW': node['SHOW'],
                'HIDE': node['HIDE']
            },
            df=Y_df
        )

        cnt_done += 1
        # print("%d/ %d Done!" % (cnt_done, len(data)))

    print("Done!")

    X = X_df.as_matrix(columns=features)
    Y = Y_df.as_matrix(columns=labels)
    # N = np.array(N_list)

    return X, N, Y


def load_json(path: str):
    """

    :param path:    The path to load the data from

    :return:        The resulting data
    """

    with open(path, 'rb') as f:
        data = json.load(f)

    return data
