# -*- coding: utf-8 -*-
"""implement logon plugin functionality."""
from __future__ import unicode_literals, print_function

from gcdt.gcdt_logging import logging_config, getLogger
from gcdt import gcdt_signals, GcdtError

from .utils import read_gcdt_awsume_file, get_last_used_role, \
    get_time_left, read_aws_config
from .awsume_main import GCDT_AWSUME_FILE, MIN_TIME_TO_EXPIRATION, AWS_CREDS_PATH, DURATION
from .awsume import renew


log = getLogger(__name__)


def check_credentials(params):
    """Check credentials are valid and refresh if necessary
    :param params: context, config (context - the _awsclient, etc..
                   config - for all tools (kumo, tenkai, ...))
    """
    context, config = params
    # add plugin related values to context
    context['aws_creds_path'] = AWS_CREDS_PATH
    context['gcdt_awsume_file'] = GCDT_AWSUME_FILE
    context['duration'] = DURATION

    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    account, account_details = get_last_used_role(roles)

    expiration = account_details['expiration']
    if expiration < MIN_TIME_TO_EXPIRATION:
        config = read_aws_config(context['aws_creds_path'])
        renew(context, config)
    else:
        log.info('Your credentials will expire in %s seconds.', get_time_left(expiration))

    # add account & expiration to context
    context['expiration'] = expiration
    context['account'] = account


def register():
    """Please be very specific about when your plugin needs to run and why.
    E.g. run the sample stuff after at the very beginning of the lifecycle
    """
    gcdt_signals.check_credentials_init.connect(check_credentials)


def deregister():
    gcdt_signals.check_credentials_init.disconnect(check_credentials)
