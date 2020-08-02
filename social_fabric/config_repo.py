#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import json
from shutil import rmtree, copytree


class ConfigNetwork:
    NETWORK_NAME = 'sf-network'
    ATTACH_NAME  = 'sf-attach'

class ConfigRepo:

    # --- Global ---
    DATA_REPO    = None
    BIN_REPO     = 'bin'  # FIX_ME
    LOG_REPO     = 'log'
    ACCESS_DIR   = '.access'
    ACCESS_KEY   = '.access/key'
    ACCESS_SALT  = '.access/salt'
    ACCESS_FILE  = '.access/passwd'

    # --- Network Specific ---
    NETWORK_NAME = ConfigNetwork.NETWORK_NAME
    NETWORK_REPO = ConfigNetwork.NETWORK_NAME

    # --- Examples ---
    EXAMPLE_NETWORK_REPO = 'example-network'
    EXAMPLE_NETWORK_CONFIG_REPO = 'example-network/config'
    EXAMPLE_NETWORK_TEMPLATES_REPO = 'example-network/templates'
    EXAMPLE_ATTACH_CONFIG_REPO = 'example-attach/config'
    EXAMPLE_ATTACH_TEMPLATES_REPO = 'example-attach/templates'

    # --- Sources ---
    TEMPLATE_SRC_DIR   = ConfigNetwork.NETWORK_NAME + os.sep + 'templates'
    FABIC_CA_SRC_REPO  = ConfigNetwork.NETWORK_NAME + os.sep + 'architecture' + os.sep + 'fabric-ca'
    ORDERER_SRC_REPO   = ConfigNetwork.NETWORK_NAME + os.sep + 'architecture' + os.sep + 'ordererOrganizations'
    PEER_SRC_REPO      = ConfigNetwork.NETWORK_NAME + os.sep + 'architecture' + os.sep + 'peerOrganizations'

    # --- Targets ---
    TARGET_REPO           = ConfigNetwork.NETWORK_NAME + os.sep + 'organizations'
    FABIC_CA_TARGET_REPO  = ConfigNetwork.NETWORK_NAME + os.sep + 'organizations/fabric-ca'
    ORDERER_TARGET_REPO   = ConfigNetwork.NETWORK_NAME + os.sep + 'organizations/ordererOrganizations'
    PEER_TARGET_REPO      = ConfigNetwork.NETWORK_NAME + os.sep + 'organizations/peerOrganizations'

    CONFIGTX_REPO         = ConfigNetwork.NETWORK_NAME + os.sep + 'configtx'
    CONFIG_REPO           = ConfigNetwork.NETWORK_NAME + os.sep + 'config'
    DOCKER_REPO           = 'docker'
    CHANNEL_REPO          = 'channels'

    @classmethod
    def set_directories(cls, config):
        cls.BIN_REPO = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'bin'
        cls.DATA_REPO = config['DATA_PATH']
        cls.LOG_REPO = config['LOG_PATH']

    @classmethod
    def set_network(cls, network):

        # --- Network Specific ---
        cls.NETWORK_NAME = network
        cls.NETWORK_REPO = network

        # --- Examples ---
        cls.EXAMPLE_NETWORK_REPO           = cls.DATA_REPO + os.sep + 'example-network'
        cls.EXAMPLE_NETWORK_CONFIG_REPO    = cls.DATA_REPO + os.sep + 'example-network/config'
        cls.EXAMPLE_NETWORK_TEMPLATES_REPO = cls.DATA_REPO + os.sep + 'example-network/templates'
        cls.EXAMPLE_ATTACH_CONFIG_REPO     = cls.DATA_REPO + os.sep + 'example-attach/config'
        cls.EXAMPLE_ATTACH_TEMPLATES_REPO  = cls.DATA_REPO + os.sep + 'example-attach/templates'

        # --- Sources ---
        cls.TEMPLATE_SRC_DIR  = network + os.sep + 'templates'
        cls.FABIC_CA_SRC_REPO = network + os.sep + 'architecture' + os.sep + 'fabric-ca'
        cls.ORDERER_SRC_REPO  = network + os.sep + 'architecture' + os.sep + 'ordererOrganizations'
        cls.PEER_SRC_REPO     = network + os.sep + 'architecture' + os.sep + 'peerOrganizations'

        # --- Targets ---
        cls.TARGET_REPO          = network + os.sep + 'organizations'
        cls.FABIC_CA_TARGET_REPO = network + os.sep + 'organizations/fabric-ca'
        cls.ORDERER_TARGET_REPO  = network + os.sep + 'organizations/ordererOrganizations'
        cls.PEER_TARGET_REPO     = network + os.sep + 'organizations/peerOrganizations'
        cls.CONFIGTX_REPO        = network + os.sep + 'configtx'
        cls.CONFIG_REPO          = network + os.sep + 'config'
        cls.CHANNEL_REPO         = 'channels'
        cls.DOCKER_REPO          = 'docker'

    @classmethod
    def create_source_dir(cls):
        os.makedirs(cls.NETWORK_REPO)
        os.makedirs(cls.FABIC_CA_SRC_REPO)
        os.makedirs(cls.ORDERER_SRC_REPO)
        os.makedirs(cls.PEER_SRC_REPO)

    @classmethod
    def save_working_conf(cls, mode, directory):
        with open('config' + os.sep + 'working.json', 'w') as f:
            json.dump({'mode': mode, 'directory': directory}, f)

    @classmethod
    def load_working_conf(cls):
        if os.path.exists('config' + os.sep + 'working.json'):
            with open('config' + os.sep + 'working.json', 'r') as f:
                conf_dict = json.load(f)
                return conf_dict['mode'], conf_dict['directory']

        return None, None

    @classmethod
    def set_working_mode(cls, working_mode):

        returned_mode = None

        if working_mode == 'CreateWithExample':

            returned_mode = 'CreateNetwork'
            cls.set_network(ConfigNetwork.NETWORK_NAME)
            copytree(cls.EXAMPLE_NETWORK_REPO, cls.NETWORK_REPO)
            ConfigRepo.save_working_conf(returned_mode, ConfigNetwork.NETWORK_NAME)

        elif working_mode == 'Create':

            returned_mode = 'CreateNetwork'
            cls.set_network(ConfigNetwork.NETWORK_NAME)
            cls.create_source_dir()
            copytree(cls.EXAMPLE_NETWORK_CONFIG_REPO, cls.CONFIG_REPO)
            copytree(cls.EXAMPLE_NETWORK_TEMPLATES_REPO, cls.TEMPLATE_SRC_DIR)
            ConfigRepo.save_working_conf(returned_mode, ConfigNetwork.NETWORK_NAME)

        elif working_mode == 'Attach':

            returned_mode = 'AttachOrganizations'
            cls.set_network(ConfigNetwork.ATTACH_NAME)
            cls.create_source_dir()
            copytree(cls.EXAMPLE_ATTACH_CONFIG_REPO, cls.CONFIG_REPO)
            copytree(cls.EXAMPLE_ATTACH_TEMPLATES_REPO, cls.TEMPLATE_SRC_DIR)
            ConfigRepo.save_working_conf(returned_mode, ConfigNetwork.ATTACH_NAME)

        return returned_mode