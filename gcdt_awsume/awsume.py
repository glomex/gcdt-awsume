# -*- coding: utf-8 -*-
"""implement logon commands."""
from __future__ import unicode_literals, print_function
import os

from gcdt.gcdt_logging import logging_config, getLogger

from .utils import create_awsclient, write_aws_config, \
    write_gcdt_awsume_file, read_gcdt_awsume_file, get_last_used_role, \
    chunker
from .aws_mfa import get_credentials, validate_credentials
from .utils import decode_format_timestamp


log = getLogger(__name__)


def renew(context, config):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    account, account_details = get_last_used_role(roles)

    profile = account_details['profile']
    assumed_role = account_details['assumed_role']
    username = account_details['username']
    expiration = account_details['expiration']

    log.info("Refreshing credentials for {}".format(assumed_role))
    # output time until expiration
    #print(get_time_left(expiration))

    create_awsclient(context, profile)
    expiration = get_credentials(
        context, config, profile, assumed_role, username)
    write_gcdt_awsume_file(context, account, profile, assumed_role, username, expiration)
    write_aws_config(context, config, expiration)
    log.info(
        "Success! Your credentials will expire in %s seconds at: %s"
        % (context['duration'], decode_format_timestamp(expiration)))


def set_account(context, config, account, assumed_role, profile, username):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    _, account_details = get_last_used_role(roles)

    if username is None:
        if not account_details:
            log.error('First time users need to provide a username via \'--username\'')
            return 1
        else:
            username = account_details['username']

    log.info("Using account {}".format(account))

    create_awsclient(context, profile)
    if not validate_credentials(config, profile, assumed_role):
        expiration = get_credentials(
            context, config, profile, assumed_role, username)
        write_gcdt_awsume_file(context, account, profile, assumed_role, username, expiration)
        write_aws_config(context, config, expiration)
        log.info(
            "Success! Your credentials will expire in %s seconds at: %s"
            % (context['duration'], decode_format_timestamp(expiration)))


def list_accounts(context):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    log.info('You configured access to the following AWS accounts:')
    for chunk in chunker(roles.keys(), 5):
        log.info(', '.join(chunk))


def switch(context, config, account=None):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    if account not in roles:
        log.error('Account \'%s\' not set. Please use \'logon set\' to fix that.')
        return 1
    account_details = roles[account]
    profile = account_details['profile']
    username = account_details['username']
    assumed_role = account_details['assumed_role']

    if not account:
        if os.environ.get('AWS_ACCOUNT_NAME', None):
            # switch back to configured account
            account = os.environ.get('AWS_ACCOUNT_NAME')
        else:
            log.error("Please provide account name or set AWS_ACCOUNT_NAME env")
            return 1

    create_awsclient(context, profile)
    log.info("Switching into {} account".format(account))
    expiration = get_credentials(context, config, profile, assumed_role, username)
    write_gcdt_awsume_file(context, account, profile, assumed_role, username, expiration)
    write_aws_config(context, config, expiration)
    log.info(
        "Success! Your credentials will expire in %s seconds at: %s"
        % (context['duration'], decode_format_timestamp(expiration)))
