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


def histogram_dataset_distribution(cnt):
    """

            Method that prints a histogram of the distribution of node types
        present in our dataset

    :return:
    """

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

#new_data = get_data()

data = {
    'File': 1226165,
    'Process': 46419,
    'Socket': 45507,
    'Meta': 17089,
    'Machine': 25,
    'Pipe': 66848
}

#for n in data:
#    data[n] += new_data[n]

#print(data)

histogram_dataset_distribution(data)
