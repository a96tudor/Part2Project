import numpy as np

class Model:
    def __init__(self):
        self._x = 0

    def print_msg(self, *args):
        """
            Private method that prints a message to the console

        :param args:        the messages to be printed, line by line
        :return:            -
        """
        for arg in args[0]:
            if isinstance(arg, str):
                print(arg)
            else:
                # It is a tuple

                print(arg[0] % arg[1])

    def get_stats(self, results, correctYs):
        """

        :param results:         a list of length n of dictionaries, each one having the format:
                                    {
                                        "SHOW": <TRUE/ FALSE>
                                        "HIDE": <TRUE/ FALSE>
                                    }
        :param correctYs:       nx2 Dataframe with the two cols 'SHOW', 'HIDE'
        :return:                a dictionary with the statistical results of the evaluation
        """
        stats = dict()

        print(len(results), len(correctYs))

        stats["correct_classifications"] = 0
        stats["true_positive"] = 0
        stats["true_negative"] = 0
        stats["false_positive"] = 0
        stats["false_negative"] = 0

        print(correctYs.columns.values)

        for idx in range(len(results)):

            if not results[idx]['HIDE'] and not results[idx]['SHOW']:
                # If this happens, we want to show the node just to be sure that it's all ok
                results[idx]['SHOW'] = True

            if correctYs.iloc[idx,:].loc['HIDE'] == 1 and results[idx]['HIDE']:
                # IT'S A CORRECT HIDE CLASSIFICATION
                stats["correct_classifications"] += 1
                stats["true_negative"] += 1
                continue

            if correctYs.iloc[idx,:].loc['SHOW'] == 1 and results[idx]['SHOW']:
                # IT'S A CORRECT SHOW CLASSIFICATION
                stats["correct_classifications"] += 1
                stats["true_positive"] += 1
                continue

            print(results[idx])

            if results[idx]['SHOW']:
                # FALSE POSITIVE
                stats["false_positive"] += 1
                continue

            if results[idx]['HIDE']:
                # FALSE NEGATIVE
                stats["false_negative"] += 1
                continue

        stats["precision"] = stats["true_positive"] / (stats["true_positive"] + stats["false_positive"])
        stats["recall"] = stats["true_positive"] / (stats["true_positive"] + stats["false_negative"])

        stats["f1_score"] = 2 * (stats["precision"] * stats["recall"]) / (stats["precision"] + stats["recall"])

        s1, s2, s3, s4 = stats["true_positive"] + stats["false_positive"],\
                         stats["true_negative"] + stats["false_negative"],\
                         stats["true_negative"] + stats["false_positive"], \
                         stats["true_positive"] + stats["false_negative"]

        print("%d tp %d fp %d tn %d fn" % (stats['true_positive'], stats['false_positive'], stats['true_negative'], stats['false_negative']))

        stats["mcc_score"] = (stats["true_positive"] * stats["true_negative"] - stats["false_negative"] * stats["false_positive"]) \
                             / np.sqrt(s1 * s2 * s3 * s4)

        stats["accuracy"] = stats["correct_classifications"] / len(results)

        return stats
