# -*- coding: utf-8 -*-
"""A gcdt-plugin to implement logon for AWS accounts."""
from __future__ import unicode_literals, print_function
import sys
import datetime
import logging

import botocore.exceptions
import botocore.session
import configparser
from backports.configparser import NoOptionError

from .utils import datetime_to_timestamp, get_time_left, create_awsclient, \
    write_session_to_gcdt_awsume_file, read_gcdt_awsume_file, get_last_used_role

log = logging.getLogger(__name__)


def get_user_session(context):
    data = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    account, account_details = get_last_used_role(data['roles'])
    username = account_details['username']

    profile = account_details['profile']
    create_awsclient(context, profile)

    # read session token from file
    user_session = data.get('sessions', {}).get(username, {})
    session_expiration = user_session.pop('Expiration', None)
    # output time until expiration
    #print(get_time_left(session_expiration))
    if get_time_left(session_expiration) < 3610:
        log.info("Refreshing session token for {}".format(username))
        # session valid <60 min
        # create new session token
        user_session = get_session_token(context, username)
        # save session token
        user_session['Expiration'] = datetime_to_timestamp(user_session['Expiration'])
        write_session_to_gcdt_awsume_file(context, username, user_session)
        user_session.pop('Expiration', None)

    return user_session, account, account_details


def get_session_token(context, username):
    """Obtain token using MFA."""
    mfa_device = "arn:aws:iam::976167517828:mfa/{}".format(username)
    try:
        token_input = raw_input
    except NameError:
        token_input = input

    mfa_token = token_input('Enter AWS MFA code for device [%s] '
                            '(renewing for %s seconds):' %
                            (mfa_device, context['duration']))

    client_sts = context['_awsclient'].get_client('sts')
    try:
        response = client_sts.get_session_token(
            DurationSeconds=36000,
            SerialNumber=mfa_device,
            TokenCode=mfa_token
        )
        return response['Credentials']
    except botocore.exceptions.ClientError as exc:
        log.error(exc)


# code from here: https://github.com/broamski/aws-mfa/blob/master/aws-mfa
def get_credentials(context, config, user_session, profile, assumed_role):
    session_role_name = profile

    client_sts = context['_awsclient'].get_client('sts', **user_session)
    try:
        response = client_sts.assume_role(
            RoleArn=assumed_role,
            RoleSessionName=session_role_name,
            DurationSeconds=context['duration'],
        )

        config.set(
            profile,
            'assumed_role',
            'True',
        )
        config.set(
            profile,
            'assumed_role_arn',
            assumed_role
        )
    except botocore.exceptions.ClientError as exc:
        log.error(exc)
        sys.exit(1)
        #return 1

    # aws_session_token and aws_security_token are both added
    # to support boto and boto3
    options = [
        ('aws_access_key_id', 'AccessKeyId'),
        ('aws_secret_access_key', 'SecretAccessKey'),
        ('aws_session_token', 'SessionToken'),
        ('aws_security_token', 'SessionToken'),
    ]

    for option, value in options:
        config.set(
            profile,
            option,
            response['Credentials'][value]
        )

    # Save expiration individually, so it can be manipulated
    config.set(
        profile,
        'expiration',
        response['Credentials']['Expiration'].strftime('%Y-%m-%d %H:%M:%S')
    )
    return datetime_to_timestamp(response['Credentials']['Expiration'])


def validate_credentials(config, profile, assumed_role):
    """Validate credentials

    :param config:
    :param profile:
    :param assumed_role:
    :return: True if credentials are still valid, else False
    """
    reup_message = "Obtaining credentials for a new role or profile."
    # Validate presence of short-term section
    if not config.has_section(profile):
        log.info("Short term credentials (profile) section %s is missing, "
                    "obtaining new credentials." % (profile,))
        if profile == 'default':
            configparser.DEFAULTSECT = profile
            if sys.version_info.major == 3:
                config.add_section(profile)
            config.set(profile, 'CREATE', 'TEST')
            config.remove_option(profile, 'CREATE')
        else:
            config.add_section(profile)
        return False
    # Validate option integrity of short-term section
    else:
        required_options = ['assumed_role',
                            'aws_access_key_id', 'aws_secret_access_key',
                            'aws_session_token', 'aws_security_token',
                            'expiration']
        try:
            short_term = {}
            for option in required_options:
                short_term[option] = config.get(profile, option)
        except NoOptionError:
            log.warn("Your existing credentials are missing or invalid, "
                        "obtaining new credentials.")
            return False
        try:
            current_role = config.get(profile, 'assumed_role_arn')
        except NoOptionError:
            current_role = None
        # There are not credentials for an assumed role,
        # but the user is trying to assume one
        if current_role is None and assumed_role:
            log.info(reup_message)
            return False
        # There are current credentials for a role and
        # the role arn being provided is the same.
        elif (current_role is not None and
              assumed_role and current_role == assumed_role):
            exp = datetime.datetime.strptime(
                config.get(profile, 'expiration'), '%Y-%m-%d %H:%M:%S')
            diff = exp - datetime.datetime.utcnow()
            if diff.total_seconds() <= 0:
                log.info("Your credentials have expired, renewing.")
                return False
            else:
                log.info(
                    "Your credentials are still valid for %s seconds, your role ARN is %s"
                    " they will expire at %s"
                    % (diff.total_seconds(), assumed_role, exp))
        # There are credentials for a current role and the role
        # that is attempting to be assumed is different
        elif (current_role is not None and
              assumed_role and current_role != assumed_role):
            log.info(reup_message)
            return False
        # There are credentials for a current role and no role arn is
        # being supplied
        elif current_role is not None and assumed_role is None:
            log.info(reup_message)
            return False
        else:
            exp = datetime.datetime.strptime(
                config.get(profile, 'expiration'), '%Y-%m-%d %H:%M:%S')
            diff = exp - datetime.datetime.utcnow()
            if diff.total_seconds() <= 0:
                log.info("Your credentials have expired, renewing.")
                return False
            else:
                log.info(
                    "Your credentials are still valid for %s seconds, your role ARN is %s"
                    " they will expire at %s"
                    % (diff.total_seconds(), assumed_role, exp))
                return True
