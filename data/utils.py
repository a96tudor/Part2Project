import pandas as pd
import numpy as np


def read_data_from_csv(file, label_cols, drop_cols=None, split=True):
    """

    :param file:            Path to the csv file where to read the data from
    :param drop_cols:       List of columns to be dropped from the read data. Default None
    :param label_cols:      List of columns that specify labels
    :param split:           If we also want to split the data into training/testing set or not

    :return:                The data, either as an np.ndarray or as a pd.DataFrame
                            By 'the data', I mean a pair (X, Y) where X are the features and Y are the labels
    """

    df = pd.read_csv(file)

    if drop_cols is not None:
        df = df.drop(drop_cols)

    if split:
        return split_dataframe(df, label_cols)

    df_Ys = df.loc[:, label_cols]

    df_Xs = df.loc[:, list(set(df.columns.values) - set(label_cols))]

    return df_Xs, df_Ys


def split_dataframe(df, label_cols, percentile=.75):
    """

    :param df:              the dataframe we want to split
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
    idx_1st = np.random.choice(rows_cnt, size=rows_cnt_1st)
    idx_2nd = list(set(range(rows_cnt)) - set(idx_1st))

    df_1st_Xs = df.iloc[idx_1st, X_cols]
    df_1st_Ys = df.iloc[idx_1st, Y_cols]
    df_2nd_Xs = df.iloc[idx_2nd, X_cols]
    df_2nd_Ys = df.iloc[idx_2nd, Y_cols]

    return df_1st_Xs, df_1st_Ys, \
           df_2nd_Xs, df_2nd_Ys





