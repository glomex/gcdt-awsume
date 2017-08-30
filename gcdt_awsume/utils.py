# -*- coding: utf-8 -*-
"""Utils."""
from __future__ import unicode_literals, print_function
import os
import json
import logging

import botocore.session
import configparser
import maya

from gcdt.gcdt_awsclient import AWSClient


log = logging.getLogger(__name__)


def decode_format_timestamp(timestamp):
    """Convert unix timestamp (seconds) into datetime.

    :param timestamp: unix timestamp in seconds
    :return: datetime in UTC
    """
    dt = maya.MayaDT(timestamp)
    timezone = dt.local_timezone
    return maya.to_utc_offset_aware(dt.datetime(to_timezone=timezone))


def datetime_to_timestamp(dt):
    """Convert datetime to seconds since epoc.

    :param dt:
    :return: seconds since 1970-01-01
    """
    return int(maya.MayaDT.from_datetime(dt)._epoch)


def get_time_left(expiration):
    """Time left in seconds from expiration (ts).

    :param expiration:
    :return: time left in seconds
    """
    if isinstance(expiration, int):
        left = expiration - maya.now().epoch
        return max(left, 0)
    else:
        return 0


def create_awsclient(context, profile):
    profile_long_term = '{}-long-term'.format(profile)
    awsclient = AWSClient(botocore.session.Session(profile=profile_long_term))
    context['_awsclient'] = awsclient


def write_aws_config(context, config, expiration):
    with open(context['aws_creds_path'], 'w') as configfile:
        config.write(configfile)


def write_role_to_gcdt_awsume_file(context, account, profile, assumed_role,
                                   username, expiration):
    """This file we will use for refreshing creds
    """
    data = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    if 'roles' not in data:
        data['roles'] = {}

    data['roles'][account] = {
        'profile': profile,
        'assumed_role': assumed_role,
        'username': username,
        'expiration': expiration,
    }

    with open(context['gcdt_awsume_file'], 'w') as answer_file:
        answer_file.write(json.dumps(data))


def write_session_to_gcdt_awsume_file(context, username, user_session):
    """This file we will use for refreshing creds
    """
    data = read_gcdt_awsume_file(context['gcdt_awsume_file'])
    if 'sessions' not in data:
        data['sessions'] = {}

    data['sessions'][username] = user_session

    with open(context['gcdt_awsume_file'], 'w') as answer_file:
        answer_file.write(json.dumps(data))


def read_gcdt_awsume_file(answers_file_path):
    try:
        with open(answers_file_path, 'r') as answer_file:
            json_file = json.loads(answer_file.read())
        return json_file
    except IOError as exception:
        log.warn("There is no files with your last credentials.".format(exception))
        return {}


def get_last_used_role(roles):
    items = sorted(roles.items(), key=lambda a: a[1]['expiration'])
    if items:
        return items[-1]  # [0], items[-1][1]
    else:
        return None, {}


def read_aws_config(aws_creds_path):
    """Read aws config.

    :param aws_creds_path:
    :return:
    """
    if not os.path.isfile(aws_creds_path):
        log.error('Could not locate credentials file at {}'.format(
            aws_creds_path))
    else:
        config = configparser.RawConfigParser()
        config.read(aws_creds_path)
        return config


def chunker(seq, size):
    # here: https://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))
