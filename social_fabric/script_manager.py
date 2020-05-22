#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import subprocess
from time import sleep
from datetime import datetime
from social_fabric.config_repo import ConfigRepo


class ScriptManager:

    debug = False

    @classmethod
    def _execute_(cls, args, directory=None, environment=None):

        if cls.debug:
            print('executing', args, environment)

        present_dir = os.getcwd()
        if directory:
            working_dir = directory
        else:
            working_dir = present_dir

        try:
            # Add bin directory in front of others
            present_env = os.environ.copy()
            present_env['PATH'] = ConfigRepo.BIN_REPO + ':' + os.environ['PATH']

            # Change the working directory to execute code
            os.chdir(working_dir)
            if environment:
                for elem in environment:
                    present_env[elem] = environment[elem]
            subcommand = subprocess.run(args,  # universal_newlines=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        env=present_env)
            error_code = subcommand.returncode
            str_out = subcommand.stdout
            str_err = subcommand.stderr

            if cls.debug:
                print('>>>', present_env)
                print('>>>', error_code)
                print('>>>', str_out)
                print('>>>', str_err)
        except Exception as e:
            raise e
        finally:
            os.chdir(present_dir)
            sleep(0.2)

        return error_code, str_out, str_err

    def __init__(self, serialized_instance = None):
        os.makedirs(ConfigRepo.LOG_REPO, exist_ok=True)
        if serialized_instance:
            self.log_file = serialized_instance['log']
            self.instruction_list = serialized_instance['list']
        else:
            self.log_file = 'deploy-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.log'
            self.instruction_list = []

    def add(self, command, directory='', environment=''):
        self.instruction_list.append({"command": command,
                                      "directory": directory,
                                      "environment": environment})

    def next_instruction(self):
        if self.instruction_list:
            return self.instruction_list.pop(0)
        return None

    def execute(self, args, directory=None, environment=None):
        error_code, str_out, str_err = self._execute_(args, directory, environment)
        with open(ConfigRepo.LOG_REPO + os.sep + self.log_file, 'ab') as f:
            f.write(str_out + str_err)
        return error_code, str_out, str_err

    def serialize(self):
        return {'log': self.log_file, 'list': self.instruction_list }

