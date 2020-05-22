#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import json
from shutil import rmtree
from social_fabric.script_manager import ScriptManager
from social_fabric.config_repo import ConfigRepo
from social_fabric.password_manager import PasswordManager

def read_and_strip(str):
    if str:
        return str.strip()
    return None


class ComponentManager:

    def __init__(self, config, owner_manager):
        self.config = config
        self.owner_manager = owner_manager

    @staticmethod
    def _match_docker_list_(component_dict):

        component_dict['deployed'] = os.path.exists(ConfigRepo.TARGET_REPO)

        # Check status
        error_code, str_out, str_err = ScriptManager._execute_(['docker', 'ps'])
        if error_code != 0:
            return

        # reset
        working_mode, _ = ConfigRepo.load_working_conf()
        for item in component_dict['nodes']:
            node_type = item['type']
            if working_mode == 'AttachOrganizations' and node_type in ('consortium', 'orderer'):
                item['status'] = '------'
            else:
                item['status'] = 'inactive'

        # match
        lines = str_out.decode().splitlines()
        offset = lines[0].index('NAMES')
        for elem in lines[1:]:
            name = elem[offset:]
            for item in component_dict['nodes']:
                if item['addr'] == name or item['owner'] == name:
                    if working_mode == 'AttachOrganizations' and item['type'] in ('consortium', 'orderer'):
                        item['status'] = '------'
                    else:
                        item['status'] = 'active'
                    break

    def _build_component_list_(self):

        component_dict = {}
        component_list = []

        if not os.path.exists(ConfigRepo.ORDERER_SRC_REPO):
            os.makedirs(ConfigRepo.ORDERER_SRC_REPO)
        if not os.path.exists(ConfigRepo.PEER_SRC_REPO):
            os.makedirs(ConfigRepo.PEER_SRC_REPO)

        consortium_list = sorted(os.listdir(ConfigRepo.ORDERER_SRC_REPO))
        organization_list = sorted(os.listdir(ConfigRepo.PEER_SRC_REPO))

        if len(consortium_list) > 0:
            component_dict['addr'] = consortium_list[0]
            consortium_path = ConfigRepo.ORDERER_SRC_REPO + os.sep + component_dict['addr']
            consortium_dict = self._load_component_dict_(consortium_path, component_dict['addr'])
            component_list.append({'addr': consortium_list[0], 'type': 'consortium', 'name': consortium_dict['name'],
                                   'ports': consortium_dict['ports'], 'owner': consortium_dict['owner'],
                                   'password': '', 'status': 'unknown'})
            orderer_list = sorted(os.listdir(ConfigRepo.ORDERER_SRC_REPO + os.sep + component_dict['addr'] +
                                             os.sep + 'orderers'))
            for elem in orderer_list:
                orderer_path = ConfigRepo.ORDERER_SRC_REPO + os.sep + component_dict['addr'] + \
                               os.sep + 'orderers' + os.sep + elem
                orderer_dict = self._load_component_dict_(orderer_path, elem)
                component_list.append({'addr': elem, 'type': 'orderer', 'name': orderer_dict['name'],
                                       'ports': orderer_dict['ports'], 'owner': '', 'password': orderer_dict['password'],
                                       'status': 'unknown'})
            for elem in organization_list:
                organization_path = ConfigRepo.PEER_SRC_REPO + os.sep + elem
                organization_dict = self._load_component_dict_(organization_path, elem)
                component_list.append({'addr': elem, 'type': 'organization', 'name': organization_dict['name'],
                                       'ports': organization_dict['ports'], 'owner': organization_dict['owner'],
                                       'password': '', 'status': 'unknown'})
                peer_list = sorted(os.listdir(organization_path + os.sep + 'peers'))
                for peer in peer_list:
                    peer_path = organization_path + os.sep + 'peers' + os.sep + peer
                    peer_dict = self._load_component_dict_(peer_path, peer)
                    component_list.append({'addr': peer, 'type': 'peer', 'name': peer_dict['name'],
                                           'ports': peer_dict['ports'], 'owner': '', 'password': peer_dict['password'],
                                           'status': 'unknown'})

            component_dict['nodes'] = component_list

            ComponentManager._match_docker_list_(component_dict)

            return component_dict

        return {'name': '', 'addr': '', 'nodes': [], 'owners': []}

    @staticmethod
    def _find_component_path_(addr):
        consortium_list = os.listdir(ConfigRepo.ORDERER_SRC_REPO)
        for consortium in consortium_list:
            if consortium == addr:
                return ConfigRepo.ORDERER_SRC_REPO + os.sep + consortium
            orderer_list = os.listdir(ConfigRepo.ORDERER_SRC_REPO + os.sep + consortium + os.sep + 'orderers')
            for orderer in orderer_list:
                if orderer == addr:
                    return ConfigRepo.ORDERER_SRC_REPO + os.sep + consortium + os.sep + 'orderers' + os.sep + orderer
        organization_list = os.listdir(ConfigRepo.PEER_SRC_REPO)
        for org in organization_list:
            if org == addr:
                return ConfigRepo.PEER_SRC_REPO + os.sep + org
            peer_list = os.listdir(ConfigRepo.PEER_SRC_REPO + os.sep + org + os.sep + 'peers')
            for peer in peer_list:
                if peer == addr:
                    return ConfigRepo.PEER_SRC_REPO + os.sep + org + os.sep + 'peers' + os.sep + peer
        return None

    @staticmethod
    def _save_component_dict_(component_dict, component_path, addr):
        filename = component_path + os.sep + addr + '.json'
        with open(filename, 'w') as f:
            json.dump(component_dict, f)

    @staticmethod
    def _load_component_dict_(component_path, addr):
        filename = component_path + os.sep + addr + '.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                component_dict = json.load(f)
        else:
            component_dict = {"addr": addr, "name": "", "ports": "", "password": "", "owner": ""}
            with open(filename, 'w') as f:
                json.dump(component_dict, f)
        return component_dict

    def _return_list_(self):
        component_dict = self._build_component_list_()
        for node in component_dict['nodes']:
            if node['password']:
                node['password'] = PasswordManager.DISPLAYED_PASS
        _, owner_list = self.owner_manager.get_owner_list()
        component_dict['owners'] = owner_list
        return None, component_dict

    # ---- Public Methods ----

    def attach_orderer(self, consortium_name, consortium_addr, orderer_name, orderer_addr, orderer_ports, orderer_cert):
        # Consortium
        full_path = ConfigRepo.ORDERER_SRC_REPO + os.sep + consortium_addr
        if os.path.exists(full_path):
            return 'Consortium ' + consortium_addr + ' already exists'
        os.mkdir(full_path)
        os.mkdir(full_path + os.sep + 'orderers')
        os.mkdir(full_path + os.sep + 'users')
        self.set_name(consortium_addr, consortium_name)

        # Orderer
        full_path = ConfigRepo.ORDERER_SRC_REPO + os.sep + consortium_addr + os.sep + 'orderers' + os.sep + orderer_addr
        if os.path.exists(full_path):
            return 'Orderer ' + orderer_addr + ' already exists'
        os.mkdir(full_path)
        os.mkdir(full_path + os.sep + 'msp')
        os.mkdir(full_path + os.sep + 'msp' + os.sep + 'tlscacerts')
        msg, _ = self.set_name(orderer_addr, orderer_name)
        if msg:
            return msg, None
        with open(full_path + os.sep + 'msp' + os.sep + 'tlscacerts' + os.sep + 'tlsca.' + consortium_addr + '-cert.pem', 'w') as f:
            f.write(orderer_cert)
        msg, component_dict = self.set_ports(orderer_addr, orderer_ports)

        return msg, component_dict

    def add_consortium(self, name, addr):
        full_path = ConfigRepo.ORDERER_SRC_REPO + os.sep + addr
        if os.path.exists(full_path):
            return 'Consortium ' + addr + ' already exists'
        os.mkdir(full_path)
        os.mkdir(full_path + os.sep + 'ca')
        os.mkdir(full_path + os.sep + 'msp')
        os.mkdir(full_path + os.sep + 'tls')
        os.mkdir(full_path + os.sep + 'orderers')
        os.mkdir(full_path + os.sep + 'users')

        return self._return_list_()

    def add_orderer(self, consortium, addr):
        full_path = ConfigRepo.ORDERER_SRC_REPO + os.sep + consortium + os.sep + 'orderers' + os.sep + addr
        if os.path.exists(full_path):
            return 'Orderer ' + addr + ' already exists'
        os.mkdir(full_path)
        os.mkdir(full_path + os.sep + 'msp')
        os.mkdir(full_path + os.sep + 'tls')
        return self._return_list_()

    def add_organization(self, consortium, addr):
        full_path = ConfigRepo.PEER_SRC_REPO + os.sep + addr
        if os.path.exists(full_path):
            return 'Organization ' + addr + ' already exists'
        os.mkdir(full_path)
        os.mkdir(full_path + os.sep + 'ca')
        os.mkdir(full_path + os.sep + 'msp')
        os.mkdir(full_path + os.sep + 'tls')
        os.mkdir(full_path + os.sep + 'peers')
        os.mkdir(full_path + os.sep + 'users')
        return self._return_list_()

    def add_peer(self, consortium, org_addr, peer_addr):
        full_path = ConfigRepo.PEER_SRC_REPO + os.sep + org_addr + os.sep + 'peers' + os.sep + peer_addr
        if os.path.exists(full_path):
            return 'Peer ' + peer_addr + ' already exists'
        os.mkdir(full_path)
        os.mkdir(full_path + os.sep + 'msp')
        os.mkdir(full_path + os.sep + 'tls')
        return self._return_list_()

    def set_name(self, addr, name):
        component_path = ComponentManager._find_component_path_(addr)
        if not component_path:
            return 'Component address ' + addr + ' not found', None
        component_dict = ComponentManager._load_component_dict_(component_path, addr)
        component_dict['name'] = name
        ComponentManager._save_component_dict_(component_dict, component_path, addr)
        return self._return_list_()

    def set_ports(self, addr, ports):
        component_path = ComponentManager._find_component_path_(addr)
        if not component_path:
            return 'Component address ' + addr + ' not found', None
        component_dict = ComponentManager._load_component_dict_(component_path, addr)
        component_dict['ports'] = ports
        ComponentManager._save_component_dict_(component_dict, component_path, addr)
        return self._return_list_()

    def set_password(self, addr, password):
        component_path = ComponentManager._find_component_path_(addr)
        if not component_path:
            return 'Component address ' + addr + ' not found', None
        component_dict = ComponentManager._load_component_dict_(component_path, addr)
        component_dict['password'] = PasswordManager.encrypt(password)
        ComponentManager._save_component_dict_(component_dict, component_path, addr)
        return self._return_list_()

    def set_owner(self, addr, owner):
        component_path = ComponentManager._find_component_path_(addr)
        if not component_path:
            return 'Component address ' + addr + ' not found', None
        component_dict = ComponentManager._load_component_dict_(component_path, addr)
        component_dict['owner'] = owner
        ComponentManager._save_component_dict_(component_dict, component_path, addr)
        return self._return_list_()

    def remove_node(self, addr):
        component_path = ComponentManager._find_component_path_(addr)
        if not component_path:
            return 'Component address ' + addr + ' not found', None
        rmtree(component_path)
        return self._return_list_()

    def refresh_status(self, component_dict):
        self._match_docker_list_(component_dict)

    def get_node_list(self):
        return self._return_list_()

    def get_clear_node_list(self):
        component_dict = self._build_component_list_()
        _, owner_list = self.owner_manager.get_clear_owner_list()
        component_dict['owners'] = owner_list
        return component_dict
