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
        for args in args:
            if isinstance(args, str):
                print(args)
            else:
                # It is a tuple
                print(args[0] % args[1])

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

        stats["correct_classifications"] = 0
        stats["true_positive"] = 0
        stats["true_negative"] = 0
        stats["false_positive"] = 0
        stats["false_negative"] = 0

        for idx in range(len(results)):

            if correctYs[idx, 'HIDE'] == 1 and results[idx]['HIDE']:
                # IT'S A CORRECT HIDE CLASSIFICATION
                stats["correct_classifications"] += 1
                stats["true_negative"] += 1
                continue

            if correctYs[idx, 'SHOW'] == 1 and results[idx]['SHOW']:
                # IT'S A CORRECT SHOW CLASSIFICATION
                stats["correct_classifications"] += 1
                stats["true_positive"] += 1
                continue

            if correctYs[idx, 'HIDE'] == 1 and results[idx]['SHOW']:
                # FALSE POSITIVE
                stats["false_positive"] += 1

            if correctYs[idx, 'SHOW'] == 1 and results[idx]['HIDE']:
                # FALSE NEGATIVE
                stats["false_negative"] += 1

        stats["precision"] = stats["true_positive"] / (stats["true_positive"] + stats["false_positive"])
        stats["recall"] = stats["true_positive"] / (stats["true_positive"] + stats["false_negative"])

        stats["f1_score"] = 2 * (stats["precision"] * stats["recall"]) / (stats["precision"] + stats["recall"])

        s1, s2, s3, s4 = stats["true_positive"] + stats["false_positive"],\
                         stats["true_negative"] + stats["false_negative"],\
                         stats["true_negative"] + stats["false_positive"], \
                         stats["true_positive"] + stats["false_negative"]

        stats["mcc_score"] = (stats["true_positive"] * stats["true_negative"] - stats["false_negative"] * stats["false_positive"]) \
                             / np.sqrt(s1 * s2 * s3 * s4)

        stats["accuracy"] = stats["correct_classifications"] / len(results)

        return stats
