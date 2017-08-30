import os
import pytest
import botocore.session
import configparser
from gcdt_testtools.placebo_awsclient import PlaceboAWSClient
from generate_creds.utils import read_roles_file
from generate_creds.validate import get_role_arn, validate_credentials
from gcdt_testtools.helpers_aws import cleanup_buckets, awsclient
from gcdt_testtools.helpers import temp_folder  # fixture!

ANSWER_FILE = os.path.join(os.path.dirname(__file__), 'testdata/answer.json')
AWS_CREDS_PATH = os.path.join(os.path.dirname(__file__), 'testdata/credentials')
ACCOUNT_ID = '111111111111'
ROLES_URL = 'http://noname.com'
TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testdata/role_list.json')


'''
@pytest.fixture()
def read_file():
    content = read_roles_file(TESTDATA_FILENAME)
    return content
'''


def test_get_role_arn():
    current_account = 'pnb-dev'
    current_role = 'superuser'
    expected_role_arn = 'arn:aws:iam::028693506758:role/7f-selfassign-super/pnb-dev-SuperUser-JVE51W2EKZ3B'
    role_arn = get_role_arn(current_account, current_role, TESTDATA_FILENAME)
    assert role_arn == expected_role_arn


'''
@pytest.fixture(scope='function')  # 'function' or 'module'
def awsclient(request, temp_folder):
    prefix = request.module.__name__ + '.' + request.function.__name__
    record_dir = os.path.join(temp_folder[0], 'placebo_awsclient', prefix)
    if not os.path.exists(record_dir):
        os.makedirs(record_dir)

    client = PlaceboAWSClient(botocore.session.Session(), data_path=record_dir)
    yield client
'''


def test_record(awsclient):
    config = configparser.RawConfigParser()
    config.read(AWS_CREDS_PATH)
    assumed_role = 'arn:aws:iam::028693506758:role/7f-selfassign-super/pnb-dev-SuperUser-JVE51W2EKZ3B'
    username = 'maksym.sotnikov'
    args = {}
    args['--duration'] = 3600
    args['--dry-run'] = False
    args['--log-level'] = 'DEBUG'
    validate_credentials(args, config, assumed_role, username, ANSWER_FILE, AWS_CREDS_PATH)
    # asserts ???
