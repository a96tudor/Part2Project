import argparse, sys
from data.training import generate_training_set, split_training_set


def build_training_set(args):
    """
        Function that takes the appropriate actions in order to build the training set

    :param args:            A dictionary containing the required arguments for building the training set
    :return:                -
    """
    """
    generate_training_set(
        host=args['host'],
        port=args['port'],
        db_usrname=args['user'],
        db_passwd=args['pass'],
        rules_path=args['rules'],
        training_set_path=args['set']
    )
    """

    split_training_set()


def train_data(args):
    """
            Function that takes the appropriate actions in order to train the model

        :param args:            A dictionary containing the required arguments for training the model
        :return:                -
    """
    print("Training...")


def evaluate(args):
    """
            Function that takes the appropriate actions in order to evaluate the model

        :param args:            A dictionary containing the required arguments for evaluating the model
        :return:                -
    """
    print("Evaluating...")


def classify(args):
    """
                Function that takes the appropriate actions in order to classify a single node

            :param args:            A dictionary containing the required arguments for classifying a single node
            :return:                -
    """
    print("Classifying...")


_COMMAND_ACTION = {
    'get_training_set': build_training_set,
    'train': train_data,
    'eval': evaluate,
    'classify': classify
}


def parser_setup():
    """
        Method that sets-up an arguments parser

    :return:        the ArgumentParser object
    """
    parser = argparse.ArgumentParser(prog='main')

    subparsers = parser.add_subparsers(help='Sub-commands help:', dest='command')


    # Creating subparser for building training set
    parser_training_set = subparsers.add_parser('get_training_set',
                                                help='Sub-command used to build the training set'
                                                )

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
                                         help='Sub-command for training the data',
                                        )

    parser_train.add_argument('--set',
                              default='data/training/training_set.csv',
                              help='Path where to read the training set from. Default data/training/training_set.csv.')


    # Creating the subparser for evaluating a single node
    parser_classify = subparsers.add_parser('classify',
                                             help='Sub-command for classifying a single node'
                                            )

    parser_classify.add_argument('--host',
                                 default='127.0.0.1',
                                 help='Host where the Neo4J database runs on. Default 127.0.0.1')

    parser_classify.add_argument('--port',
                                     type=int,
                                     default=7474,
                                     help='Port number where the Neo4J database runs on. Default 7474')

    parser_classify.add_argument('--node',
                                     help='ID of the node we want to evaluate')


    # Creating the subparser for evaluating the entire model
    parser_evaluate = subparsers.add_parser('eval',
                                            help='Sub-command for evaluating the entire model',
                                           )

    return parser


if __name__ == '__main__':
    parser = parser_setup()
    args = parser.parse_args()
    args = vars(args)
    if len(args) == 0:
        parser.print_help()
        sys.exit()
    elif len(args) == 1:
        parser.print_help()
        sys.exit()
    else:
        for key in args:
            if args[key] is None:
                parser.print_help()
                sys.exit()

        # Otherwise, all good, we can continue

        _COMMAND_ACTION[args['command']](args)
