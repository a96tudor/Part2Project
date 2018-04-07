import pandas as pd
import matplotlib.pyplot as plt
import data.training.constants as cnst
from data.training.database_driver import DatabaseDriver
import numpy as np


def get_data():
    q = dict()
    cnt = dict()

    dbDriver = DatabaseDriver(host='127.0.0.1', port=7474, usrname='neo4j', passwd='opus')

    q["File"] = "match (n:File) " \
            "return count(n)"

    q["Process"] = "match (n:Process) " \
               "return count(n)"

    q["Socket"] = "match (n:Socket) " \
              "return count(n)"

    q["Meta"] = "match (n:Meta) " \
            "return count(n)"


    q["Machine"] = "match (n:Machine) " \
               "return count(n)"


    q["Pipe"] = "match (n:Pipe) " \
            "return count(n)"

    for node in q:
        cnt[node] = dbDriver.execute_query(q[node])[0]['count(n)']

    return cnt


def histogram_dataset_distribution():
    """

            Method that prints a histogram of the distribution of node types
        present in our dataset

    :return:
    """

    cnt = {
        'File': 1226165,
        'Process': 46419,
        'Socket': 45507,
        'Meta': 17089,
        'Machine': 25,
        'Pipe': 66848
    }

    sizes_log = [np.log(x) for x in cnt.values()]
    sizes = list(cnt.values())
    pos = [1 + x for x in range(len(sizes))]
    labels = cnt.keys()
    total = sum(sizes)

    bar = plt.bar(pos, sizes_log, align='center')
    plt.xticks(pos, labels)
    plt.xlabel('Node types')
    plt.ylabel("Logarithm of the node's frequency")

    idx = 0

    print("{:4.2f} %".format(2.22))

    for rect in bar:
        height = rect.get_height()
        prc = float(sizes[idx] / total)
        plt.text(rect.get_x() + rect.get_width()/2.0,
                 height,
                 "{:10.5f}%".format(prc * 100),
                 ha='center',
                 va='bottom')
        idx += 1
    plt.show()

    print("Total: {:d}".format(total))


def histogram_node_degrees():

    def merge_df(df1, df2):

        result = pd.DataFrame(columns=df1.columns.values)

        idx1 = 0
        idx2 = 0

        while idx1 < len(df1) and idx2 < len(df2):

            if df1.loc[idx1, 'degree'] == df2.loc[idx2, 'degree']:
                result = result.append(
                    {
                        'degree': df1.loc[idx1, 'degree'],
                        'count': df1.loc[idx1, 'count'] + df2.loc[idx2, 'count']
                    }, ignore_index=True
                )
                idx1 += 1
                idx2 += 1
            elif df1.loc[idx1, 'degree'] < df2.loc[idx2, 'degree']:
                result = result.append(
                    {
                        'degree': df1.loc[idx1, 'degree'],
                        'count': df1.loc[idx1, 'count']
                    }, ignore_index=True
                )

                idx1 += 1
            else:
                result = result.append(
                    {
                        'degree': df2.loc[idx2, 'degree'],
                        'count': df2.loc[idx2, 'count']
                    }, ignore_index=True
                )

                idx2 += 1

        while idx1 < len(df1):
            result = result.append(
                {
                    'degree': df1.loc[idx1, 'degree'],
                    'count': df1.loc[idx1, 'count']
                }, ignore_index=True
            )

            idx1 += 1

        while idx2 < len(df2):
            result = result.append(
                {
                    'degree': df2.loc[idx2, 'degree'],
                    'count': df2.loc[idx2, 'count']
                }, ignore_index=True
            )

            idx2 += 1

        return result

    df1 = pd.read_csv('csv/degree_dataset1.csv')
    df2 = pd.read_csv('csv/degree-dataset2.csv')
    df3 = pd.read_csv('csv/degree-dataset3.csv')

    full = merge_df(merge_df(df1, df2), df3)

    data = list()

    for i in range(len(full)):
        for _ in range(full.loc[i, 'count']):
            data.append(full.loc[i, 'degree'])

    plt.hist(data, bins=len(full))
    plt.title('Log-scale histogram of node degrees')
    plt.xlabel('Node degree')
    plt.ylabel('Number of nodes')
    plt.yscale('log', nonposy='clip')
    plt.show()


histogram_node_degrees()