[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](http://sre-docs.glomex.cloud/glomex-checks/index.html)
[![License](http://img.shields.io/badge/license-MIT-yellowgreen.svg)](LICENSE) 
[![GitHub issues](https://img.shields.io/github/issues/glomex/glomex-cloud-deployment-tools.svg?maxAge=2592000)](https://github.com/glomex/glomex-cloud-deployment-tools/issues)

TODO: add tests
TODO: fix docs


# Plugin for gcdt

author: glomex SRE Team
gcdt: https://github.com/glomex/gcdt

This script makes it easy to manage your AWS SDK Security Credentials when Multi-Factor Authentication (MFA) is enforced on your AWS account. It automates the process of obtaining temporary credentials from the AWS Security Token Service and updating your AWS Credentials file (located at ~/.aws/credentials).

Features include:

* create temporary token to access an AWS account
* switch between accounts
* allow gcdt to check remaining time until expired
* renew token as part of the gcdt lifecycle


## Installation
***
Download this folder and do
```sh
$ pip install -r requirements.txt
$ python setup.py install
```


## Initial setup
**Set ENV variable AWS_DEFAULT_PROFILE or script will use "default" profile**
```bash
$ export AWS_DEFAULT_PROFILE=glomex
```


## Credentials File Setup
***
In a typical AWS credentials file (located at ~/.aws/credentials), credentials are stored in sections, denoted by a pair of brackets: []. The [default] section stores your default credentials. You can store multiple sets of credentials using different profile names. If no profile is specified, the [default] section is always used.

Long term credential sections are identified by the convention [<profile_name>-long-term]. Short term credentials are identified by the typical convention: [<profile_name>]. The following illustrates how you would configure you credentials file using this script:
```sh
[glomex-long-term]
aws_access_key_id = YOUR_LONGTERM_KEY_ID
aws_secret_access_key = YOUR_LONGTERM_ACCESS_KEY
```

After running the awsume command, your credentials file would read:
```sh
[glomex-long-term]
aws_access_key_id = YOUR_LONGTERM_KEY_ID
aws_secret_access_key = YOUR_LONGTERM_ACCESS_KEY

[glomex]
aws_access_key_id = <POPULATED_BY_SCRIPT>
aws_secret_access_key = <POPULATED_BY_SCRIPT>
aws_security_token = <POPULATED_BY_SCRIPT>
```


## Usage
***

```sh
Usage:
  generate_creds.py show-roles <account>
  generate_creds.py generate [--duration=<sec>] [--log-level=<set>] [--account=<name>]
                            [--access=<level>] [--username=<user>] [--non-interactive]
                            [--dry-run]
  generate_creds.py refresh  [--dry-run]
  generate_creds.py (-h | --help)
  generate_creds.py --version

Commands:
   show-roles        Show list of roles. Specify 'all' to see list of all roles for all accounts.
                     Specify account name 'pnb-stage' to see only roles for this account
   generate          Generate STS credentials in interactive mode
   refresh           Refresh last used credentials

Options:
  -h --help             Show this screen.
  --account=<name>      AWS account to generate STS credentials.
                        Could provided via the environment variable 'AWS_ACCOUNT_NAME'.
  --username=<user>     Username that you use in AWS 'firstname.lastname'.
                        Could provided via the environment variable 'AWS_USER_NAME'.
  --access=<level>      Level of access (developer|superuser|readonly) [default: developer].
  --duration=<sec>      The duration, in seconds, that the
                        temporary credentials should remain valid.
                        Could provided via the environment variable 'MFA_STS_DURATION'
                        [default: 3600].
  --non-interactive     Generate credentials without interactive mode using command line options
                        or ENV variables.
  --dry-run             List all values to stdout without changing credentials file
  --log-level=<set>     Set log level. 'CRITICAL', 'ERROR', 'WARNING',
                        'INFO', 'DEBUG', 'NOTSET' [default: DEBUG].
```


## Usage example
***
If you don't know the account and access what you need you can use:
```sh
$ generate-credentials show-roles all #list all account
$ generate-credentials show-roles pnb-dev #show only for pnb-dev account
```
To generate new credentials in interactive mode:
```sh
$ generate-credentials generate
```
Or use command args without interactive mode:
```bash
$ generate-credentials generate --account pnb-dev --username firstname.lastname --access superuser --non-interactive
```
Also you can specify all options like ENV variables and run only:
```sh
$ generate-credentials generate --non-interactive
```
Use dry-run command to get on stdout all information without changing ~/.aws/credentials file
```sh
$ generate-credentials generate --dry-run
```
Script has refresh function. After first successfully running script remember all info that you type in interactive mode and save into `~/.aws/answer.json`. If you want to refresh it just do:
```bash
$ $ generate-credentials refresh
```


## Example outputs
***
Output with --dry-run command
```sh
INFO - You roles file is up to date. Continue...
INFO - Obtaining credentials for a new role or profile.
Enter AWS MFA code for device [arn:aws:iam::976167517828:mfa/firstname.lastname] (renewing for 3600 seconds):957064
assumed_role True
assumed_role_arn arn:aws:iam::028693506758:role/7f-selfassign-super/pnb-dev-SuperUser-JVE51W2EKZ3B
aws_access_key_id <VALUE>
aws_secret_access_key <VALUE>
aws_session_token <VALUE>
aws_security_token <VALUE>
expiration 2017-05-30 09:10:07
```
Output without dry-run command
```sh
INFO - You roles file is up to date. Continue...
INFO - Obtaining credentials for a new role or profile.
Enter AWS MFA code for device [arn:aws:iam::976167517828:mfa/firstname.lastname] (renewing for 3600 seconds):984935
INFO - Success! Your credentials will expire in 3600 seconds at: 2017-05-30 09:09:51+00:00
```
Output if you forgot to specify some options and didn't set any ENV variable for it
```sh
INFO - You roles file is up to date. Continue...
ERROR - Please provide account-name or set AWS_ACCOUNT_NAME env
```


## Running tests
Please make sure to have good test coverage for your plugin so we can always make sure your plugin runs with the upcoming gcdt version.

Run tests like so:

``` bash
$ python -m pytest -vv --cov-report term-missing tests/test_*
```


## License
Copyright (c) 2017 glomex and others.
gcdt and plugins are released under the MIT License (see LICENSE).
