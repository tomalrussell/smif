"""
"""
import logging
import os
import sys
from argparse import ArgumentParser

__author__ = "Will Usher"
__copyright__ = "Will Usher"
__license__ = "mit"

logger = logging.getLogger(__name__)

_log_format = '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s'
logging.basicConfig(filename='cli.log',
                    level=logging.DEBUG,
                    format=_log_format,
                    filemode='a')


def setup_project_folder(project_path):
    """Creates folder structure in the target directory

    Arguments
    =========
    project_path : str
        Absolute path to an empty folder

    """
    folder_list = ['assets', 'config', 'planning']
    for folder in folder_list:
        if os.path.exists(folder):
            msg = "The {} folder already exists, skipping...".format(folder)
            logger.info(msg)
        else:
            msg = "Creating {} folder in {}".format(folder, project_path)
            logger.info(msg)
            os.mkdir(folder)


def setup_configuration(args):
    """Sets up the configuration files into the defined project folder

    """

    print("Arguments: {}".format(args))
    project_path = os.path.abspath(args.path)
    msg = "Set up the project folders in {}?".format(project_path)
    response = confirm(msg,
                       response=False)
    if response:
        msg = "Setting up the project folders in {}".format(project_path)
        logger.info(msg)
        setup_project_folder(project_path)
    else:
        logger.info("Setup cancelled.")


def run_model(args):
    """Runs the model specified in the args.model argument

    """
    if args.model == 'all':
        logger.info("Running the system of systems model")
    else:
        logger.ingo("Running the {} sector model".format(args.model))


def parse_arguments(args, list_of_sector_models):
    """

    Arguments
    =========
    args : list
        Command line arguments
    list_of_sector_models : list
        A list of sector model names

    """

    parser = ArgumentParser(description='Command line tools for smif')

    subparsers = parser.add_subparsers()

    parser_setup = subparsers.add_parser('setup',
                                         help='Setup the project folder')
    parser_setup.set_defaults(func=setup_configuration)
    parser_setup.add_argument('path',
                              help="Path to the project folder")

    parser_run = subparsers.add_parser('run',
                                       help='Run a model')
    parser_run.set_defaults(func=run_model)

    run_model_list = list_of_sector_models.extend('all')

    parser_run.add_argument('model',
                            choices=run_model_list,
                            help='The name of the model to run')

    return parser


def confirm(prompt=None, response=False):
    """Prompts for a yes or no response from the user

    Arguments
    =========
    prompt : str, default=None
    response : bool, default=False


    Returns
    =======
    bool
        True for yes and False for no.


    Notes
    =====

    `response` should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', response=True)
    Create Directory? [y]|n:
    True
    >>> confirm(prompt='Create Directory?', response=False)
    Create Directory? [n]|y:
    False
    >>> confirm(prompt='Create Directory?', response=False)
    Create Directory? [n]|y: y
    True

    """

    if prompt is None:
        prompt = 'Confirm'

    if response:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        ans = input(prompt)
        if not ans:
            return response
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def main(arguments=None):
    list_of_sector_models = ['water_supply', 'solid_waste']
    parser = parse_arguments(arguments, list_of_sector_models)
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main(sys.argv[1:])
