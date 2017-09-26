# -*- coding: utf-8 -*-
"""implement logon commands."""
from __future__ import unicode_literals, print_function
import os

from gcdt.gcdt_logging import logging_config, getLogger

from .utils import create_awsclient, write_aws_config, \
    write_role_to_gcdt_awsume_file, read_gcdt_awsume_file, get_last_used_role, \
    chunker
from .aws_mfa import validate_credentials, \
    get_user_session, get_credentials
from .utils import decode_format_timestamp


log = getLogger(__name__)


def renew(context, config):
    """renew credentials for last used role

    :param context:
    :param config:
    :return:
    """
    user_session, account, account_details = get_user_session(context)

    username = account_details['username']
    profile = account_details['profile']

    # assume role
    assumed_role = account_details['assumed_role']
    log.info('Refreshing credentials for \'%s\' role', assumed_role)
    role_expiration = get_credentials(
        context, config, user_session, profile, assumed_role)
    write_role_to_gcdt_awsume_file(context, account, profile, assumed_role, username, role_expiration)
    write_aws_config(context, config, role_expiration)
    log.info(
        "Your credentials will expire in %s seconds at: %s"
        % (context['duration'], decode_format_timestamp(role_expiration)))


def set_account(context, config, account, assumed_role, profile, username):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])['roles']
    _, account_details = get_last_used_role(roles)

    if username is None:
        if not account_details:
            log.error('First time users need to provide a username via \'--username\'')
            return 1
        else:
            username = account_details['username']

    log.info('Using account \'%s\'', account)

    create_awsclient(context, profile)
    if not validate_credentials(config, profile, assumed_role):
        user_session, _, _ = get_user_session(context)
        expiration = get_credentials(
            context, config, user_session, profile, assumed_role)
        write_role_to_gcdt_awsume_file(context, account, profile, assumed_role, username, expiration)
        write_aws_config(context, config, expiration)
        log.info(
            "Your credentials will expire in %s seconds at: %s"
            % (context['duration'], decode_format_timestamp(expiration)))


def list_accounts(context):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])['roles']
    log.info('You configured access to the following AWS accounts:')
    for chunk in chunker(roles.keys(), 5):
        log.info(', '.join(chunk))


def clean_cache_file(context):
    log.info('Deleting cache file for gcdt-awsume....')
    cache_file = context.get('gcdt_awsume_file', None)
    if cache_file is not None:
        os.unlink(cache_file)


def switch(context, config, account=None):
    roles = read_gcdt_awsume_file(context['gcdt_awsume_file'])['roles']
    if account not in roles:
        log.error('Account \'%s\' not set. Please use \'awsume set\' to fix that.', account)
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
            log.error('Please provide account name or set AWS_ACCOUNT_NAME env')
            return 1

    user_session, _, _ = get_user_session(context)
    create_awsclient(context, profile)
    log.info('Using account \'%s\'', account)
    log.info('Switching into \'%s\' role', assumed_role)
    expiration = get_credentials(context, config, user_session, profile, assumed_role)
    write_role_to_gcdt_awsume_file(context, account, profile, assumed_role, username, expiration)
    write_aws_config(context, config, expiration)
    log.info(
        "Your credentials will expire in %s seconds at: %s"
        % (context['duration'], decode_format_timestamp(expiration)))
