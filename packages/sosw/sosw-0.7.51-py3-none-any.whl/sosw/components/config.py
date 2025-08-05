"""
..  hidden-code-block:: text
    :label: View Licence Agreement <br>

    sosw - Serverless Orchestrator of Serverless Workers

    The MIT License (MIT)
    Copyright (C) 2025  sosw core contributors <info@sosw.app>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

Config manager component. Has methods for getting configuration for Lambdas.

The default is ``DynamoConfig``. It is automatically called from the ``app.Processor.__init__`` and if your Lambda
has permissions to access  the ``config`` table, the Processor will look for the record: ``YOUR_FUNCTION_NAME_config``,
and recursively  update the ``DEFAULT_CONFIG`` with it.

You can also import and use the following functions.
They can be directly imported from this module and will be automatically switched to DDB / SSM / Secrets manager.

- get_config_
- get_credentials_by_prefix_
- get_secrets_credentials_
- update_config_

..  warning::

    Using these methods requires the Role to have relevant permissions to access DynamoDB / SSM Parameter Store /
    AWS Secrets.

Usage example `(pseudo code)`:

..  code-block:: python

    from SOME_DB_DRIVER import connect
    from sosw.components.config import get_secrets_credentials, get_config, update_config
    from sosw.app import Processor as SoswProcessor

    class Processor(SoswProcessor):

        def work_with_db(self):

            db_settings = get_credentials_by_prefix('db_')
            db_password = get_secrets_credentials(type='name', value='db_password')['db_password']

            connection = connect(**db_settings, password=db_password)

            last_processed_row = get_config('last_row')

            db_result = connection.query(f"SOME QUERY LIMIT last_processed_row, 10;")
            self.do_something(db_result)

            update_config('last_row', last_processed_row + 10)

"""

__all__ = ['ConfigSource', 'get_config', 'update_config', 'get_credentials_by_prefix', 'get_secrets_credentials']
__author__ = "Sophie Fogel, Nikolay Grishchenko"
__version__ = "1.7.3"

try:
    from aws_lambda_powertools import Logger

    logger = Logger(child=True)

except ImportError:
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

import boto3
import json
import os

from sosw.components.helpers import chunks, recursive_update
from sosw.components.dynamo_db import DynamoDbClient


class SecretsManager:
    secretsmanager_client = None


    def __init__(self, test=False, **kwargs):

        self.test = test

        if not self.test:
            self.test = True if os.environ.get('STAGE') == 'test' or os.environ.get('autotest') == 'True' else False


    def _get_secretsmanager_client(self):

        if self.secretsmanager_client is None:
            self.secretsmanager_client = boto3.client('secretsmanager')

        return self.secretsmanager_client


    def call_boto_secrets_with_pagination(self, f: str, **kwargs) -> list:
        """
        Invoke SecretsManager functions with the ability to paginate results.

        ..  _get_secrets_credentials:

        :param f:   SecretsManager function to invoke.

        :return:    If the function can be the paginate the response will return as paginate iterator.
                    Else it will return as a list
        """

        secretsmanager_client = self._get_secretsmanager_client()

        func = getattr(secretsmanager_client, f)
        can_paginate = getattr(secretsmanager_client, 'can_paginate')(f)

        if can_paginate:
            logger.debug("SecretsManager.%s can natively paginate", f)
            paginator = secretsmanager_client.get_paginator(f)
            response = paginator.paginate(**kwargs)
            return response

        else:
            logger.debug("SecretsManager.%s can not natively paginate", f)
            response_list = []
            response = func(**kwargs)
            response_list.append(response)
            while 'NextToken' in response:
                kwargs['NextToken'] = response['NextToken']
                response_list.append(func(**kwargs))
            return response_list


    def get_secrets_credentials(self, **kwargs) -> dict:
        """

        Retrieve the credentials with given name or tag from AWS SecretsManager and return as a dictionary.

        Must provide ``type`` and ``value`` to search. Type is either ``'tag'`` or ``'name'``. ``value`` is a string.

        Usage example:

        ..  code-block:: python

            my_secret =  get_secrets_credentials(type='name', value='my_secret_name')

            my_secrets_by_tag = get_secrets_credentials(type='tag', value='project_a_credentials')
        """

        filters, secrets_dict = [], {}
        filter_type, value = kwargs.get('type'), kwargs.get('value')
        valid_types = ['tag', 'name']

        if not filter_type or filter_type not in valid_types:
            raise KeyError('Error no type Tag/Name provided')

        if not value:
            raise KeyError('Error no value provided')

        filters = [{'Key': 'name', 'Values': [value]}] if filter_type == 'name' else \
            [{'Key': 'tag-value', 'Values': [value]}]

        secretsmanager_client = self._get_secretsmanager_client()

        secret_response = self.call_boto_secrets_with_pagination('list_secrets', Filters=filters)
        secrets = [secret for secret in secret_response for secret in secret['SecretList']]

        if secrets:
            for secret in secrets:
                secret_value = secretsmanager_client.get_secret_value(SecretId=secret['ARN'])
                secrets_dict[secret['Name']] = secret_value['SecretString']
        else:
            logger.warning('No credentials found in SecretsManager for %s with %s', filter_type, value)
            return secrets_dict

        return secrets_dict


class SSMConfig:
    """
    Methods to access some configurations and/or credentials stored in AWS SSM ParameterStore.
    Please note that SSM has a pretty low limit of concurrent calls and it THROTTLES.
    For high load Lambdas it is recommended to use DynamoConfig instead.
    """

    ssm_client = None


    def __init__(self, test=False, **kwargs):

        self.test = test

        if not self.test:
            self.test = True if os.environ.get('STAGE') == 'test' or os.environ.get('autotest') == 'True' else False


    def _get_ssm_client(self):

        if self.ssm_client is None:
            self.ssm_client = boto3.client('ssm')

        return self.ssm_client


    def get_config(self, name):
        """
        Retrieve the Config from AWS SSM ParameterStore and return as a JSON parsed dictionary.

        :param str name:    Name of config to extract
        :rtype:             dict
        :return:            Config of some Controller
        """

        ssm_client = self._get_ssm_client()

        try:
            response = ssm_client.get_parameters(
                Names=[name],
                WithDecryption=True
            )
        except Exception:
            response = ssm_client.get_parameters(
                Names=[name],
                WithDecryption=False
            )

        try:
            config = json.loads(response['Parameters'][0]['Value'])
        except (KeyError, IndexError, TypeError):
            config = {}

        return config


    def update_config(self, name, val, **kwargs):
        """
        Update a parameter in SSM ParameterStore with a new value.

        :param  str     name:   Parameter name to address.
        :param  object  val:    Parameter value to update.
        """

        description = kwargs.get('description')
        if not isinstance(description, str):
            description = ''

        param_type = kwargs.get('param_type')
        if param_type not in ('String', 'StringList', 'SecureString'):
            param_type = 'String'

        ssm_client = self._get_ssm_client()
        ssm_client.put_parameter(
            Name=name,
            Description=description,
            Value=val,
            Type=param_type,
            Overwrite=True
        )


    def call_boto_with_pagination(self, f, **kwargs) -> list:
        """
        Invoke SSM functions with the ability to paginate results.

        :param str f:           SSM function to invoke.
        :param object kwargs:   Keyword arguments for the function to invoke.
        """

        ssm_client = self._get_ssm_client()

        func = getattr(ssm_client, f)
        can_paginate = getattr(ssm_client, 'can_paginate')(f)

        if can_paginate:
            logger.debug("'SSM.%s()' can natively paginate", f)
            paginator = ssm_client.get_paginator(f)
            response = paginator.paginate(**kwargs)
            return list(response)

        else:
            logger.debug("'SSM.%s()' can not natively paginate", f)
            response_list = []
            response = func(**kwargs)
            response_list.append(response)
            while 'NextToken' in response:
                kwargs['NextToken'] = response['NextToken']
                response_list.append(func(**kwargs))
            return response_list


    def get_credentials_by_prefix(self, prefix):
        """
        Retrieve the credentials with given `prefix` from AWS SSM ParameterStore and return as a dictionary.

        In ParameterStore the values `Name` must begin with `prefix_` and they must have Tag:Environment `(production|dev)`.
        The type of elements is expected to be SecureString. Regular strings could work, but not guaranteed.

        :param str prefix:  prefix of records to extract
        :rtype:             dict
        :return:            Some credentials
        """

        env_tag = 'production' if not self.test else 'dev'
        prefix = prefix if prefix.endswith('_') else prefix + '_'

        describe_params_response = self.call_boto_with_pagination('describe_parameters',
                                                                  ParameterFilters=[
                                                                      {"Key": "tag:Environment", "Values": [env_tag]},
                                                                      {
                                                                          'Key':    'Name', 'Option': 'BeginsWith',
                                                                          'Values': [prefix]
                                                                      }])

        logger.debug("SSM.describe_parameters(prefix=%s) received response: %s", prefix, describe_params_response)
        params = [param for obj in describe_params_response for param in obj['Parameters']]

        names = [param['Name'] for param in params]
        if not names:
            logger.warning(
                "No credentials found in SSM ParameterStore with prefix %s for Environment: %s", prefix, env_tag)
            return dict()

        # This is supposed to work fine if you ask multiple keys even if some are not encrypted.
        # Anyway you should encrypt everything.
        decryption_required = any([True for param in params if param['Type'] == 'SecureString'])

        result = dict()
        for chunk_of_names in chunks(names, 10):
            get_params_response = self.call_boto_with_pagination('get_parameters', Names=chunk_of_names,
                                                                 WithDecryption=decryption_required)
            logger.debug(f"SSM.get_parameters(names=%s) received response: %s", chunk_of_names, get_params_response)

            # Update keys and values from this page of response to result. Removes the prefix away for keys.
            params = [param for obj in get_params_response for param in obj['Parameters']]
            if params:
                result.update(dict([(x['Name'].replace(prefix, ''), x['Value'] if x['Value'] != 'None' else None)
                                    for x in params]))

        return result


class DynamoConfig:
    """
    This is a manager to operate with custom configurations for Lambdas stored in the ``config`` DynamoDB table.
    It tries to find the table ``config`` in the same region where the Lambda runs with the following structure:

    ..  code-block:: python

        'env':          'S',
        'config_name':  'S',
        'config_value': 'S',

    If the table exists and the Lambda has permissions to access it, the class will look for the record:
    ``YOUR_FUNCTION_config``, and recursively update the ``DEFAULT_CONFIG`` with it.

    .. _get_config:
    """

    dynamo_client: DynamoDbClient = None
    no_ddb_access: bool = None


    def __init__(self, **kwargs):

        self.test = kwargs.get('test')
        if not self.test:
            self.test = True if os.environ.get('STAGE') == 'test' or os.environ.get('autotest') == 'True' else False

        self.config = {
            'dynamo_client_config': {
                'row_mapper':      {
                    'env':          'S',
                    'config_name':  'S',
                    'config_value': 'S'
                },
                'required_fields': ['env', 'config_name', 'config_value'],
                'table_name':      'config' if not self.test else 'autotest_config',
                # 'region': TODO IMPLEMENT AS AN OPTIONAL PARAMETER FOR app.Processor
            }
        }

        self.config = recursive_update(self.config, kwargs.get('config', {}))


    def get_config(self, name, env="production"):
        """
        Retrieve the Config from DynamoDB ``config`` table and return as a JSON parsed dictionary.
        If not in JSON format, returns a string.

        ..  note::

            In case the environment is ``test`` the table name will be automatically changed to ``autotest_config``.
            This might be relevant only for complex integration tests.

        :param str name:    Name of config to extract
        :param str env:     Environment name, usually: 'production' or 'dev'
        :rtype:             dict|string
        :return:            Configuration

        ..  _update_config:
        """

        if dynamo_client := self._get_dynamo_client():

            items = dynamo_client.get_by_query(keys={'env': env, 'config_name': name})
            item = items[0] if items else None
            config_value = item.get('config_value') if item else None
            logger.debug("Got config value from DDB: %s", config_value)
            try:
                return json.loads(config_value)
            except (json.JSONDecodeError, TypeError) as err:
                return config_value if config_value is not None else {}
        else:
            logger.info("Tried to get DynamoConfig, but failed.")
        return {}


    def update_config(self, name, val, **kwargs):
        """
        Update a field in the DynamoDB ``config`` table with a new value. May be used to store not sensitive tokens.

        ..  warning: For sensitive credentials use SecretsManager!

        ..  _get_credentials_by_prefix:

        :param  str     name:   Field name to address.
        :param  object  val:    Field value to update.
        """

        if self.test or os.environ.get('STAGE') in ['test', 'autotest']:
            env = "dev"
        else:
            env = "production"

        dynamo_client = self._get_dynamo_client()
        dynamo_client.update(keys={'env': env, 'config_name': name}, attributes_to_update={'config_value': val})


    def get_credentials_by_prefix(self, prefix: str, env: str = 'production') -> dict:
        """
        Fetches multiple records from the ``config`` table. Filters rows that start with the prefix and returns them
        as a dict with this prefix trimmed.

        ..  warning: For sensitive credentials use SecretsManager!

        Example in ``config`` DDB:

        ..  code-block:: python

            {'env': 'production', 'config_name': 'project_a_db_username', 'config_value': 'john'}
            {'env': 'production', 'config_name': 'project_a_db_port', 'config_value': '27019'}
            {'env': 'production', 'config_name': 'another_db_username', 'config_value': 'silver'}


            credentials = get_credentials_by_prefix('project_a_db')

            # {'username': 'john', 'port': '27019'}
        """


        prefix = prefix if prefix.endswith('_') else prefix + '_'

        if self.test or prefix.startswith('autotest_'):
            env = "dev"

        res = {}
        if dynamo_client := self._get_dynamo_client():
            items = dynamo_client.get_by_query(keys={'env': env, 'config_name': prefix},
                                               comparisons={'config_name': 'begins_with'})
            for row in items:
                try:
                    row['config_value'] = json.loads(row['config_value'])
                except (json.JSONDecodeError, TypeError):
                    pass
                config_name = row['config_name'].replace(prefix, '')
                res[config_name] = row['config_value']

        return res


    def _get_dynamo_client(self):
        if self.dynamo_client is None and not self.no_ddb_access:
            dynamo_config = self.config.get('dynamo_client_config')

            try:
                self.dynamo_client = DynamoDbClient(dynamo_config)
            except Exception as err:
                logger.warning("Failed to initialize DynamoDB client for ConfigSource: %s", err)
                self.no_ddb_access = True

        return self.dynamo_client


class ConfigSource:
    """
    A strategy adapter for config. Returns config from the selected config source.
    You can implement your own functions using these clients, and they can even call different configurations.

    :param str sources:     Config clients to initialize. Supported: `SSM` and `Dynamo` (default).
                            Could be both, comma-separated. The first one then becomes default.

    :param dict config:     Custom configurations for clients. Should be in `ssm_config`, `dynamo_config`, etc.
                            Don't be confused, but sometimes configs also need their own configs. :)
    """

    SUPPORTED_SOURCES = ('Dynamo', 'SSM')


    def __init__(self, test=False, sources=None, config=None, **kwargs):

        self.test = test or True if os.environ.get('STAGE') == 'test' else False

        if not sources:
            sources = ['Dynamo']

        elif isinstance(sources, str):
            sources = [x.strip() for x in sources.split(',')]

        else:
            raise ValueError(f"Unsupported sources: {sources}. Must be a csv or string of {self.SUPPORTED_SOURCES}")

        assert all(x in self.SUPPORTED_SOURCES for x in sources), f"Unsupported sources: {sources}. Must be a csv or " \
                                                                  f"string of {self.SUPPORTED_SOURCES}"

        # Overwrite default configs with custom ones if provided.
        self.config = {}
        self.config.update(config or {})

        self.default_source = None
        for source in sources:

            # Config of Config Client
            cfg = self.config.get(f"{source.lower()}_config", {})

            # Config Client class
            cls = globals()[f"{source}Config"](config=cfg, test=self.test, **kwargs)

            # Set instance of Config Client as attribute of current ConfigSource object.
            setattr(self, f"{source.lower()}_config", cls)

            if not self.default_source:
                self.default_source = getattr(self, f"{source.lower()}_config")
                logger.info("Initialized default_source = %s_config", source.lower())

        self.secrets_manager_class = SecretsManager()


    def get_config(self, name, **kwargs):
        return self.default_source.get_config(name, **kwargs)


    def update_config(self, name, val, **kwargs):
        return self.default_source.update_config(name, val, **kwargs)


    def get_credentials_by_prefix(self, prefix, **kwargs):
        return self.default_source.get_credentials_by_prefix(prefix, **kwargs)


    def get_secrets_credentials(self, **kwargs):
        return self.secrets_manager_class.get_secrets_credentials(**kwargs)


test = True if os.environ.get('STAGE') == 'test' else False

__config_source = ConfigSource(test=test)

get_config = __config_source.get_config
update_config = __config_source.update_config
get_credentials_by_prefix = __config_source.get_credentials_by_prefix
get_secrets_credentials = __config_source.get_secrets_credentials
