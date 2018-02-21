import pandas as pd
import numpy as np
from sklearn.utils import shuffle


def read_data_from_csv(file, label_cols, drop_cols=None, split=True, normalize=True):
    """
    :param file:            Path to the csv file where to read the data from
    :param drop_cols:       List of columns to be dropped from the read data. Default None
    :param label_cols:      List of columns that specify labels
    :param split:           If we also want to split the data into training/testing set or not. Default True
    :param normalize:       If we want the data we read to be normalized, by column. See normalize() for more detail.
                                Default True
    :return:                The data, either as an np.ndarray or as a pd.DataFrame
                            By 'the data', I mean a pair (X, Y) where X are the features and Y are the labels
    """

    df = pd.read_csv(file)

    print(df.iloc[0,:].loc['HIDE'])

    if drop_cols is not None:
        df = df.drop(columns=drop_cols)

    if normalize:
        df1 = df.loc[:, label_cols]
        df2 = normalize_df(df.loc[:, list(set(df.columns.values) - set(label_cols))])
        df = pd.concat([df1, df2], axis=1)

    if split:
        return split_dataframe(df, label_cols, test_part=1)

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

    #TODO: IMPLEMENT THIS
    return df


def split_dataframe(df, label_cols, test_part, percentile=0.75):
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
    test_left =  int((1-percentile)*(test_part-1)*len(df))
    test_right = int((1-percentile)*test_part*len(df) - 1)

    testDF = df.iloc[test_left:test_right, :]

    if test_left == 0:
        trainDF = df.iloc[test_right+1:, :]
    elif test_right == len(df) - 1:
        trainDF = df.iloc[:test_left-1, :]
    else:
        df1 = df.iloc[:test_left-1, :]
        df2 = df.iloc[test_right+1, :]

        trainDF = pd.concat(df1, df2, ignore_index=True)

    X_cols = list(set(df.columns.values) - set(label_cols))

    testYs = testDF.loc[:, label_cols]
    testXs = testDF.loc[:, X_cols]

    trainYs = trainDF.loc[:, label_cols]
    trainXs = trainDF.loc[:, X_cols]

    return trainXs, trainYs, testXs, testYs


def shuffle_df(df, iter=1, axis=0):
    """
        Functions that takes a path to a csv, shuffles and returns the content as a
    :param df:                  Dataframe we want to shuffle
    :return:                    -
    """
    return shuffle(df).reset_index(drop=True)
