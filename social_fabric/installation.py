#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import sys
import stat
import json
from time import sleep
from getch import getch
from shutil import copytree
from social_fabric.password_manager import PasswordManager
from social_fabric.script_manager import ScriptManager



class Install:

    images = [('hyperledger/fabric-ca',        '1.4.6'),
              ('hyperledger/fabric-tools',     '2.0.0'),
              ('hyperledger/fabric-peer',      '2.0.0'),
              ('hyperledger/fabric-orderer',   '2.0.0'),
              ('hyperledger/fabric-ccenv',     '2.0.0'),
              ('hyperledger/fabric-baseos',    '2.0.0'),
              ('hyperledger/fabric-javaenv',   '2.0.0'),
              ('hyperledger/fabric-nodeenv',   '2.0.0'),
              ('hyperledger/fabric-zookeeper', '0.4.18'),
              ('hyperledger/fabric-kafka',     '0.4.18'),
              ('hyperledger/fabric-couchdb',   '0.4.18')]

    RED       = '\033[0;31m'
    GREEN     = '\033[0;32m'
    NO_COLOUR = '\033[0m'
    DEL = '\177'
    BS  = '\b'

    @classmethod
    def _error_(cls, error_text):
        print('\n' + cls.RED + error_text + cls.NO_COLOUR, file=sys.stderr, flush=True)

    @classmethod
    def _success_(cls, success_text):
        print('\n' + cls.GREEN + success_text + cls.NO_COLOUR, flush=True)

    @classmethod
    def _info_(cls, success_text):
        print('\n' + success_text, flush=True)

    @classmethod
    def _input_password_(cls, prompt):
        print('\n' + prompt + ': ', end='', flush=True)
        response = ''
        while True:
            try:
                ch = getch()
            except:
                print(cls.RED + '\n\nconfiguration failed\n' + cls.NO_COLOUR, flush=True)
                sys.exit(-1)
            if ch == chr(13) or ch == chr(10):
                print(flush=True)
                return response
            if str(ch) == cls.BS or str(ch) == cls.DEL:  # Backspace
                if len(response) > 0:
                    response = response[:-1]
                    print(cls.BS + ' ' + cls.BS,  end='', flush=True)
            elif str(ch).isprintable():
                print('*', end='', flush=True)
                response += ch

    @classmethod
    def _input_param_(cls, question, default_value, displayed_value=None):
        if not displayed_value:
            displayed_value = default_value
        print('\n' + question + ' [' + displayed_value + ']: ', end='', flush=True)
        try:
            response = input()
        except:
            print(cls.RED + '\n\nconfiguration failed\n' + cls.NO_COLOUR, flush=True)
            sys.exit(-1)
        if not response:
            response = default_value
        return response

    @classmethod
    def _check_version_(cls, executable):
        error_code, str_out, str_err = ScriptManager._execute_([executable, '--version'])
        if error_code != 0:
            return 0, 0, None
        signature = str_out.decode('utf-8').strip('\n').strip('\r')
        content = signature.split()
        for ix, elem in enumerate(content):
            if elem.lower().startswith('version'):
                if len(content) >= ix + 1:
                    version = content[ix + 1].strip(',').split('.')
                    major = 0
                    if version[0].isdigit():
                        major = int(version[0])
                    minor = 0
                    if len(version) > 1 and version[1].isdigit():
                        minor = int(version[1])
                    return int(major), int(minor), signature
        return 0, 0, None

    @classmethod
    def _pull_and_tag_docker_image_(cls, name, version):
        error_code, str_out, str_err = ScriptManager._execute_(['docker', 'pull', name + ':' + version])
        if error_code != 0:
            cls._error_(str_err.decode('utf-8'))
            return False
        msg_out = str_out.decode('utf-8')
        cls._info_(msg_out)
        if msg_out.startswith('Status: Image is up to date'):
            return True

        # No digit version
        error_code, str_out, str_err = ScriptManager._execute_(['docker', 'tag', name + ':' + version, name])
        if error_code != 0:
            cls._error_(str_err.decode('utf-8'))
            return False
        cls._info_(str_out.decode('utf-8'))

        # Two digits version
        error_code, str_out, str_err = ScriptManager._execute_(['docker', 'tag', name + ':' + version,
                                                                name + ':' + '.'.join(version.split('.')[0:2])])
        if error_code != 0:
            cls._error_(str_err.decode('utf-8'))
            return False
        cls._info_(str_out.decode('utf-8'))

        return True

    # ---- Public Methods ----

    @classmethod
    def prerequisites(cls):
        cls._info_('\nVerifying prerequisites')

        # Docker
        major, minor, signature = cls._check_version_('docker')
        if major < 17 or (major == 17 and minor < 6):
            cls._error_('Please, install docker version 17.06.2 or above')
            return False
        cls._success_(signature + ' found')

        # Docker-compose
        major, minor, signature = cls._check_version_('docker-compose')
        if major < 1 or (major == 1 and minor < 14):
            cls._error_('Please, install docker-compose version 1.14.0 or above')
            return False
        cls._success_(signature + ' found')

        return True

    @classmethod
    def main(cls):
        response = cls._input_param_('Do you want to install and configure the application?', 'y', 'Y/n')
        if response[0].lower() == 'n':
            return

        if not cls.prerequisites():
            sys.exit(-1)

        while True:
            host = cls._input_param_('server hostname', 'localhost')
            break

        while True:
            sport = cls._input_param_('listening port', '8080')
            try:
                port = int(sport)
            except:
                cls._error_('Port must be a number above 1024')
                sleep(0.3)
                continue
            if port <= 1024:
                cls._error_('Only port number above 1024 are permitted')
                sleep(0.3)
                continue
            break

        while True:
            data_path = cls._input_param_('Data directory', os.getcwd())
            if not os.path.exists(data_path):
                create_path = cls._input_param_('data directory "' + data_path + '" does not exist. Do you want to create it?', 'y', 'Y/n')
                if create_path[0] == 'y':
                    try:
                        os.makedirs(data_path)
                        break
                    except:
                        cls._error_('Unable to create "' + data_path + '". Review path or check permissions')
                        continue
            if not os.access(data_path, os.W_OK) or not os.access(data_path, os.R_OK):
                cls._error_("You don't have read and write permission for \"" + data_path)
                continue
            break

        while True:
            log_path = cls._input_param_('Log directory', os.getcwd() + os.sep + 'log')
            if not os.path.exists(log_path):
                create_path = cls._input_param_('log directory "' + log_path + '" does not exist. Do you want to create it?', 'y', 'Y/n')
                if create_path[0] == 'y':
                    try:
                        os.makedirs(log_path)
                        break
                    except:
                        cls._error_('Unable to create "' + log_path + '". Review path or check permissions')
                        continue
            if not os.access(log_path, os.W_OK) or not os.access(data_path, os.R_OK):
                cls._error_("You don't have read and write permission for \"" + log_path)
                continue
            break

        while True:
            config_path = cls._input_param_('Path for the configuration file', os.path.join(data_path, 'config'))
            if not os.path.exists(config_path):
                create_path = cls._input_param_('Config path "' + config_path + '" does not exist. Do you want to create it?', 'y', 'Y/n')
                if create_path[0].lower() == 'y':
                    try:
                        os.makedirs(config_path)
                        break
                    except:
                        cls._error_('Unable to create "' + config_path + '". Review path or check permissions')
                        continue
            if not os.access(config_path, os.W_OK) or not os.access(data_path, os.R_OK):
                cls._error_("You don't have read and write permission for " + config_path)
                continue
            break

        secret_key = os.urandom(12).hex()

        while True:
            password = cls._input_password_('Administrator\'s password')
            msg = PasswordManager.validate(password)
            if msg:
                cls._error_(msg)
                continue
            confirm = cls._input_password_('Confirm (re-enter) password')
            if password != confirm:
                cls._error_('Password differs, please, re-enter')
                continue
            break

        # Generate keys
        PasswordManager.create_keys(data_path, password)

        # Create locally example folders (if required i.e. from pyinstaller)
        source_path = os.path.dirname(os.path.realpath(__file__))
        if source_path != os.getcwd():
            copytree(source_path + os.sep + 'example-network', data_path + os.sep + 'example-network')
            copytree(source_path + os.sep + 'example-attach', data_path + os.sep + 'example-attach')

        # Download docker images
        for image in cls.images:
            if not cls._pull_and_tag_docker_image_(image[0], image[1]):
                cls._error_('Installation failed on pulling docker images')

        # Write config file
        with open(os.path.join(config_path, 'SocialFabric.json'), 'w') as f:
            json.dump({'HOST': host,
                       'PORT': port,
                       'SECRET_KEY': secret_key,
                       'DATA_PATH': data_path,
                       'LOG_PATH': log_path,
                       'LOG_MAX_SIZE': 1000000,
                       'LOG_MAX_FILES': 10,
                       'ENV': 'production',
                       'DEBUG': False}, f)
            cls._info_('configuration file ' + os.path.join(config_path, 'SocialFabric.json') + ' created')

        # Write dockerclean.sh file
        with open(os.path.join(data_path, 'dockerclean.sh'), 'w') as f:
            f.write('#!/bin/bash\n' +
                    '\ndocker kill `docker ps -q`\n' +
                    'docker rm `docker ps -aq`\n' +
                    'docker volume prune -f\n' +
                    'docker network prune -f\n')
            os.fchmod(f.fileno(), stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            cls._info_('configuration file ' + os.path.join(data_path, 'dockerclean.sh') + ' created')

        # Write distclean.sh file
        with open(os.path.join(data_path, 'distclean.sh'), 'w') as f:
            f.write('#!/bin/bash\n' +
                    '\nrm -rf social_fabric/ors-network\n' +
                    'rm -rf social_fabric/ors-attach' +
                    'rm -f  social_fabric/log/*\n' +
                    'rm -f  social_fabric/config/working.json\n' +
                    'rm -rf social_fabric/__pycache__\n' +
                    'rm -rf SocialFabric.egg-info' +
                    'rm -rf __pycache__\n' +
                    'rm -rf dist\n')
            os.fchmod(f.fileno(), stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            cls._info_('configuration file ' + os.path.join(data_path, 'distclean.sh') + ' created')

        # Installation successful
        cls._success_('Installation and configuration completed')
        cls._success_('You may start the server with:')
        cls._info_('   ' + os.getcwd() + os.sep +
                 'SocialFabric --config ' + config_path + os.sep + 'SocialFabric.json\n')
        sys.exit(0)

if __name__ == '__main__':
    Install.main()