# -*- coding: utf-8 -*-
"""A gcdt plugin to implement logon for AWS accounts."""
from __future__ import unicode_literals, print_function
import os
import sys
from logging.config import dictConfig

from docopt import docopt
from gcdt.gcdt_cmd_dispatcher import cmd, get_command
from gcdt.gcdt_logging import logging_config, getLogger

from .utils import read_aws_config
from . import __version__
from .awsume import renew, switch, set_account, list_accounts, clean_cache_file

log = getLogger(__name__)


# TODO add config via openapi
AWS_CREDS_PATH = '%s/.aws/credentials' % (os.path.expanduser('~'),)
GCDT_AWSUME_FILE = '%s/.aws/gcdt_awsume.json' % (os.path.expanduser('~'),)
#ROLES = ['developer', 'superuser', 'readonly']
DURATION = 3600  # max in seconds
DEFAULT_PROFILE = 'glomex'
MIN_TIME_TO_EXPIRATION = 900  # TODO move to config file

# creating docopt parameters and usage help
DOC = '''Usage:
        awsume
        awsume renew
        awsume switch <account>
        awsume set <account> <arn> [--profile=<profile>] [--username=<username>]
        awsume list
        awsume clean
        awsume version

-h --help           show this
'''


@cmd(spec=['version'])
def version_cmd():
    log.info('gcdt-awsume version %s' % __version__)


@cmd(spec=['renew'])
def renew_cmd(**tooldata):
    context = tooldata.get('context')
    config = tooldata.get('config')
    return renew(context, config)


@cmd(spec=['switch', '<account>'])
def switch_cmd(account, **tooldata):
    context = tooldata.get('context')
    config = tooldata.get('config')
    return switch(context, config, account)


@cmd(spec=['list'])
def list_cmd(**tooldata):
    context = tooldata.get('context')
    return list_accounts(context)


@cmd(spec=['clean'])
def clean_cache_cmd(**tooldata):
    context = tooldata.get('context')
    return clean_cache_file(context)


@cmd(spec=['set', '<account>', '<arn>', '--profile', '--username'])
def set_cmd(account, arn, profile, username, **tooldata):
    context = tooldata.get('context')
    config = tooldata.get('config')
    if profile is None:
        profile = os.getenv('AWS_PROFILE', DEFAULT_PROFILE)
    return set_account(context, config, account, arn, profile, username)


def main():
    arguments = docopt(DOC, sys.argv[1:])
    verbose = arguments.pop('--verbose', False)
    if verbose:
        logging_config['loggers']['gcdt']['level'] = 'DEBUG'
    dictConfig(logging_config)

    command = get_command(arguments)
    if command in ['version']:
        # dispatch only
        exit_code = cmd.dispatch(arguments)
    else:
        context = {}
        context['aws_creds_path'] = AWS_CREDS_PATH
        context['gcdt_awsume_file'] = GCDT_AWSUME_FILE
        context['duration'] = DURATION
        config = read_aws_config(context['aws_creds_path'])
        if config:
            exit_code = cmd.dispatch(arguments, context=context, config=config)
        else:
            exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
