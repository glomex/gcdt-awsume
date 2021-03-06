# -*- coding: utf-8 -*-
"""implement logon plugin functionality."""
from __future__ import unicode_literals, print_function

import botocore.session
from botocore.vendored import requests
from botocore.utils import DEFAULT_METADATA_SERVICE_TIMEOUT, \
    METADATA_SECURITY_CREDENTIALS_URL, RETRYABLE_HTTP_ERRORS
from gcdt.gcdt_logging import logging_config, getLogger
from gcdt import gcdt_signals
from gcdt.gcdt_exceptions import GcdtError
from gcdt.gcdt_awsclient import AWSClient

from .utils import read_gcdt_awsume_file, get_last_used_role, \
    read_aws_config
from .awsume_main import GCDT_AWSUME_FILE, AWS_CREDS_PATH, DURATION
from .awsume import renew


log = getLogger(__name__)


def _check_running_on_ec2():
    """check if we are running on EC2"""
    # adapted from botocore/utils.py InstanceMetadataFetcher
    try:
        response = requests.get(METADATA_SECURITY_CREDENTIALS_URL,
                                timeout=DEFAULT_METADATA_SERVICE_TIMEOUT)
    except RETRYABLE_HTTP_ERRORS as e:
        log.debug("Not running on EC2 (metadataservice can not be reached)")
    else:
        if response.status_code == 200:
            return True

    return False


def renew_credentials(params):
    """assume role and renew credentials
    :param params: context, config (context - the _awsclient, etc..
                   config - for all tools (kumo, tenkai, ...))
    """
    if not _check_running_on_ec2():
        context, config = params
        # add plugin related values to context
        context['aws_creds_path'] = AWS_CREDS_PATH
        context['gcdt_awsume_file'] = GCDT_AWSUME_FILE
        context['duration'] = DURATION

        roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])['roles']
        account, account_details = get_last_used_role(roles)

        expiration = account_details['expiration']
        config = read_aws_config(context['aws_creds_path'])
        renew(context, config)
        context['_awsclient'] = AWSClient(botocore.session.Session())  # new Session

        # add account & expiration to context
        context['expiration'] = expiration
        context['account'] = account


def register():
    """Please be very specific about when your plugin needs to run and why.
    E.g. run the sample stuff after at the very beginning of the lifecycle
    """
    gcdt_signals.check_credentials_init.connect(renew_credentials)


def deregister():
    gcdt_signals.check_credentials_init.disconnect(renew_credentials)
