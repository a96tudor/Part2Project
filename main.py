import argparse


def build_training_set():
    print("Training set")


def train_data():
    print("Training...")


def evaluate():
    print("Evaluating...")


def parser_setup():
    """
        Method that sets-up an arguments parser

    :return:        the ArgumentParser object
    """
    parser = argparse.ArgumentParser(prog='main')

    subparsers = parser.add_subparsers(help='Sub-commands help:')


    # Creating subparser for building training set
    parser_training_set = subparsers.add_parser('get_training_set',
                                                help='Sub-command used to build the training set')

    parser_training_set.add_argument('--host',
                                     default='127.0.0.1',
                                     help='Host where the Neo4J database runs on. Default 127.0.0.1')

    parser_training_set.add_argument('--port',
                                     type=int,
                                     default=7474,
                                     help='Port number where the Neo4J database runs on. Default 7474')

    parser_training_set.add_argument('--user',
                                     help='Username used to connect to the Neo4J database')

    parser_training_set.add_argument('--pass',
                                     help='Password used to connect to the Neo4J database')

    parser_training_set.add_argument('--rules',
                                     default='cypher_statements/rules/',
                                     help='Path to the rule files. Default cypher_statements/rules/')

    parser_training_set.add_argument('--set',
                                     default='data/training/training_set.csv',
                                     help='Path where to create the training set file.Default data/training/training_set.csv.')


    # Creating the subparser for training data
    parser_train = subparsers.add_parser('train',
                                         help='Sub-command for training the data')

    parser_train.add_argument('--set',
                              default='data/training/training_set.csv',
                              help='Path where to read the training set from. Default data/training/training_set.csv.')


    # Creating the subparser for evaluating a single node
    parser_classify = subparsers.add_parser('classify',
                                             help='Sub-command for classifying a single node')

    parser_classify.add_argument('--host',
                                 default='127.0.0.1',
                                 help='Host where the Neo4J database runs on. Default 127.0.0.1')

    parser_classify.add_argument('--port',
                                     type=int,
                                     default=7474,
                                     help='Port number where the Neo4J database runs on. Default 7474')

    parser_training_set.add_argument('--node',
                                     help='ID of the node we want to evaluate')


    # Creating the subparser for evaluating the entire model
    parser_evaluate = subparsers.add_parser('eval',
                                            help='Sub-command for ')

    return parser


if __name__ == '__main__':
    parser = parser_setup()
    args = parser.parse_args()
    args = vars(args)
    if len(args) == 0:
        parser.print_help()