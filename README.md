[![Documentation](https://readthedocs.org/projects/gcdt/badge/?version=latest)](http://gcdt.readthedocs.io/en/latest/)
[![License](http://img.shields.io/badge/license-MIT-yellowgreen.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/glomex/gcdt.svg?maxAge=2592000)](https://github.com/glomex/gcdt/issues)


# Plugin for gcdt

author: glomex SRE Team
gcdt: https://github.com/glomex/gcdt

This plugin makes it easy to manage your AWS SDK Security Credentials when Multi-Factor Authentication (MFA) is enforced on your AWS account. It automates the process of obtaining temporary credentials from the AWS Security Token Service and updating your AWS Credentials file (located at ~/.aws/credentials).

Features include:

* create temporary credentials to access an AWS account
* switch between accounts
* allow gcdt to check remaining time until expired
* renew credentials as part of the gcdt lifecycle


## Installing the plugin

Add the following entry to the `requirements_gcdt.txt` file:
``` text
glomex-awsume
```

If you have not not activate the venv, please do so:
``` bash
$ source ./venv/bin/activate
```

And the installation step itself:
``` bash
$ pip install -r -U requirements_gcdt.txt
```


## Initial setup
**Set ENV variable AWS_DEFAULT_PROFILE or script will use "default" profile**
``` bash
$ export AWS_DEFAULT_PROFILE=glomex
```


## Credentials File Setup
In a typical AWS credentials file (located at ~/.aws/credentials), credentials are stored in sections, denoted by a pair of brackets: []. The [default] section stores your default credentials. You can store multiple sets of credentials using different profile names. If no profile is specified, the [default] section is always used.

Long term credential sections are identified by the convention [<profile_name>-long-term]. Short term credentials are identified by the typical convention: [<profile_name>]. The following illustrates how you would configure you credentials file using this script:
``` text
[glomex-long-term]
aws_access_key_id = YOUR_LONGTERM_KEY_ID
aws_secret_access_key = YOUR_LONGTERM_ACCESS_KEY
```

After running the awsume command, your credentials file would read:
``` text
[glomex-long-term]
aws_access_key_id = YOUR_LONGTERM_KEY_ID
aws_secret_access_key = YOUR_LONGTERM_ACCESS_KEY

[glomex]
aws_access_key_id = <POPULATED_BY_PLUGIN>
aws_secret_access_key = <POPULATED_BY_PLUGIN>
aws_security_token = <POPULATED_BY_PLUGIN>
```


## Usage

``` text
Usage:
    awsume
    awsume renew
    awsume switch <account>
    awsume set <account> <arn> [--profile=<profile>] [--username=<username>]
    awsume list
    awsume clean
    awsume version

-h --help           show this
```


## Usage example
If you don't know the account and access what you need you can use:
``` text
$ awsume list
```

To create a configuration for another account:
``` text
$ awsume set infra-dev arn:aws:iam::420189626185:role/7f-managed/infra-dev-TeamisFullaccess-MZSLXQ718GX6
```

For first time users create a configuration for an account:
``` text
$ awsume set infra-dev arn:aws:iam::420189626185:role/7f-managed/infra-dev-TeamisFullaccess-MZSLXQ718GX6 --profile=glomex --username=first.last
```

Or use switch to another account:
``` text
$ awsume switch infra-prod
```

Most of the time you just want to renew the last used session:
``` text
$ awsume renew
```

Also you can clean the cached account configurations:
``` text
$ awsume clean
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
