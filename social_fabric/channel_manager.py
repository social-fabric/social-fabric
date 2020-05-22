#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import json
from time import sleep
from social_fabric.config_repo import ConfigRepo
from social_fabric.script_manager import ScriptManager
from social_fabric.user_manager import UserManager
from social_fabric.deploy_manager import DeployManager

class ChannelManager:

    @staticmethod
    def _read_and_strip_(str):
        if str:
            return str.strip()
        return None

    def __init__(self):
        self.channel_list = []

    def add_channel(selfchannel_id):
        pass

    def apply_tx(self):
        pass

    @classmethod
    def read_channel_configuration(cls, component_manager, channel_id):

        component_dict = component_manager.get_clear_node_list()
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = DeployManager._get_lists_of_nodes_(component_dict)

        bcc_consortium_addr = cls._read_and_strip_(bcc_consortium_node['addr'])
        bcc_orderer_addr = cls._read_and_strip_(bcc_orderer_list[0]['addr'])  # FIX_ME: Multiple Orderer ???
        bcc_orderer_port = cls._read_and_strip_(bcc_orderer_list[0]['ports'])
        bcc_orderer_tlsca_cert = \
            '/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations/ordererOrganizations/' + \
            bcc_consortium_addr + '/orderers/' + bcc_orderer_addr + '/msp/tlscacerts/tlsca.' + \
            bcc_consortium_addr + '-cert.pem'

        for org_node in bcc_org_list:
            bcc_org_addr = cls._read_and_strip_(org_node['addr'])
            bcc_org_name = cls._read_and_strip_(org_node['name'])
            for node in bcc_peer_dict[cls._read_and_strip_(org_node['addr'])]:
                bcc_peer_addr = cls._read_and_strip_(node['addr'])
                bcc_peer_port = cls._read_and_strip_(node['ports']).split(';')[0]
                bcc_admin_addr = UserManager.find_first_admin_user(bcc_org_addr)

                # Fetching the most recent configuration block for the channel

                environment = {'CORE_PEER_TLS_ENABLED': 'true',
                               'CORE_PEER_LOCALMSPID': bcc_org_name + 'MSP',
                               'CORE_PEER_TLS_ROOTCERT_FILE': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                              bcc_org_addr + os.sep + 'peers' + os.sep +
                                                              bcc_peer_addr + '/tls/ca.crt',
                               'CORE_PEER_MSPCONFIGPATH': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                          bcc_org_addr + os.sep + 'users' + os.sep +
                                                          bcc_admin_addr + os.sep + 'msp',
                               'CORE_PEER_ADDRESS': bcc_peer_addr + ':' + bcc_peer_port,
                               'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIG_REPO}

                errorno, str_out, str_err = ScriptManager._execute_(['docker', 'exec', 'cli.' + bcc_peer_addr,
                                                                      'peer', 'channel', 'fetch', 'config',
                                                                      'config_block.pb',
                                                                      '-o', bcc_orderer_addr + ':' + bcc_orderer_port,
                                                                      '--ordererTLSHostnameOverride', bcc_orderer_addr,
                                                                      '-c', channel_id,
                                                                      '--tls',
                                                                      '--cafile', bcc_orderer_tlsca_cert],
                                                                     directory=ConfigRepo.NETWORK_NAME,
                                                                     environment=environment)
                if errorno != 0:
                    raise Exception(str_err.decode('utf-8'))

                os.makedirs(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + channel_id, exist_ok=True)
                sleep(0.2)

                errorno, str_out, str_err = ScriptManager._execute_(
                    ['docker', 'cp',
                     'cli.' + bcc_peer_addr + ':/opt/gopath/src/github.com/hyperledger/fabric/peer/config_block.pb',
                     ConfigRepo.CHANNEL_REPO + os.sep + channel_id + os.sep + 'config_block.pb'],
                    directory=ConfigRepo.NETWORK_NAME,
                    environment=environment)

                if errorno != 0:
                    raise Exception(str_err.decode('utf-8'))

                errorno, str_out, str_err = ScriptManager._execute_(
                    ['configtxlator', 'proto_decode', '--input', 'config_block.pb', '--type', 'common.Block',
                     '--output', 'config_block.json'],
                    directory=ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + channel_id)

                if errorno != 0:
                    raise Exception(str_err.decode('utf-8'))

                return # First Org, First Peer is enough

    @classmethod
    def get_list(cls, component_manager):

        channel_list = []

        os.makedirs(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO, exist_ok=True)
        for elem in os.listdir(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO):
            channel_list.append({'channel': elem, 'org': ''})
            # Always read it
            #if not os.path.exists(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + elem + os.sep + 'config_block.json'):
            cls.read_channel_configuration(component_manager, elem)
            with open(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + elem + os.sep + 'config_block.json', 'rb') as f:
                block_dict = json.load(f)
                config_dict = block_dict['data']['data'][0]['payload']['data']['config']
                org_dict = config_dict['channel_group']['groups']['Application']['groups']
                for org_name in org_dict:
                    channel_list.append({'channel': '', 'org': org_name})

        return channel_list

    @classmethod
    def export_orderer(cls, component_manager, channel_id='mychannel'):
        component_dict = component_manager.get_clear_node_list()
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = DeployManager._get_lists_of_nodes_(component_dict)

        orderer_conn_dict = {}
        orderer_conn_dict['consortium'] = {}
        bcc_consortium_addr = cls._read_and_strip_(bcc_consortium_node['addr'])
        orderer_conn_dict['consortium']['name'] = cls._read_and_strip_(bcc_consortium_node['name'])
        orderer_conn_dict['consortium']['addr'] = bcc_consortium_addr
        orderer_conn_dict['orderer'] = {}
        bcc_orderer_addr = cls._read_and_strip_(bcc_orderer_list[0]['addr'])
        orderer_conn_dict['orderer']['name'] = cls._read_and_strip_(bcc_orderer_list[0]['name'])
        orderer_conn_dict['orderer']['addr'] = bcc_orderer_addr
        orderer_conn_dict['orderer']['port'] = bcc_orderer_list[0]['ports']

        filename = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'orderers' + os.sep + \
                   bcc_orderer_addr + os.sep + 'msp' + os.sep + 'tlscacerts' + os.sep + \
                   'tlsca.' + bcc_consortium_addr +'-cert.pem'
        with open(filename, 'r') as f:
            orderer_conn_dict['orderer']['tlscacerts'] = f.read()

        return None, orderer_conn_dict

    @classmethod
    def export_organization(cls, component_manager, channel_id='mychannel'):
        component_dict = component_manager.get_clear_node_list()
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = DeployManager._get_lists_of_nodes_(component_dict)

        first = True
        org_config_txt = '{\n'
        for org_node in bcc_org_list:
            org_name = cls._read_and_strip_(org_node['name'])
            org_config_txt += '"' + org_name + 'MSP": '

            noerror, str_out, str_err = ScriptManager._execute_(['configtxgen', '-printOrg', org_name + 'MSP'],
                directory=ConfigRepo.NETWORK_NAME,
                environment={'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIGTX_REPO})
            if noerror != 0:
                raise(str_err.decode('utf-8'))

            org_config_txt += str_out.decode('utf-8')
            if first:
                first = False
            else:
                org_config_txt += ',\n'

        org_config_txt += '}\n'

        return None, org_config_txt

    @classmethod
    def create_channel(cls, component_manager, channel_id):

        component_dict = component_manager.get_clear_node_list()

        script_manager = ScriptManager()

        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = DeployManager._get_lists_of_nodes_(component_dict)

        # --- Create Channel ----
        script_manager.add(['configtxgen',
                            '-profile', 'TwoOrgsChannel',
                            '-channelID', channel_id,
                            '-outputCreateChannelTx', './channel-artifacts/' + channel_id + '.tx'],
                           directory=ConfigRepo.NETWORK_NAME,
                           environment={"FABRIC_CFG_PATH": os.getcwd() + os.sep + ConfigRepo.CONFIGTX_REPO})

        # FIX_ME: Single Org
        for node in bcc_org_list:
            bcc_org_name = cls._read_and_strip_(node['name'])
            script_manager.add(['configtxgen',
                                '-profile', 'TwoOrgsChannel',
                                '-outputAnchorPeersUpdate', './channel-artifacts/' + bcc_org_name + 'MSPanchors.tx',
                                '-channelID', channel_id,
                                '-asOrg', bcc_org_name + 'MSP'],
                               directory=ConfigRepo.NETWORK_NAME,
                               environment={"FABRIC_CFG_PATH": os.getcwd() + os.sep + ConfigRepo.CONFIGTX_REPO})

        # ---- Create channel ----

        bcc_conn_addr = 'localhost'  # FIX_ME

        bcc_consortium_addr = bcc_consortium_node['addr']
        bcc_orderer_addr = bcc_orderer_list[0]['addr']
        bcc_orderer_port = bcc_orderer_list[0]['ports']
        bcc_org_addr = bcc_org_list[0]['addr']
        bcc_org_name = bcc_org_list[0]['name']
        bcc_peer_addr = bcc_peer_dict[bcc_org_addr][0]['addr']
        ports = cls._read_and_strip_(bcc_peer_dict[bcc_org_addr][0]['ports']).split(';')
        bcc_peer_port = ports[0].strip()
        bcc_admin_addr = UserManager.find_first_admin_user(bcc_org_addr)

        # Use a stand alone peer to create the transaction
        # Configuration of the peer (core.yaml) is in ConfigRepo.CONFIG_REPO
        bcc_orderer_ca = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + \
                         bcc_consortium_addr + os.sep + 'orderers' + os.sep + bcc_orderer_addr + \
                         os.sep + 'msp/tlscacerts/tlsca.' + bcc_consortium_addr + '-cert.pem'

        environment = {'CORE_PEER_TLS_ENABLED': 'true',
                       # 'ORDERER_CA': bcc_orderer_ca,
                       'CORE_PEER_LOCALMSPID': bcc_org_name + 'MSP',
                       'CORE_PEER_TLS_ROOTCERT_FILE': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                      bcc_org_addr + os.sep + 'peers' + os.sep +
                                                      bcc_peer_addr + '/tls/ca.crt',
                       'CORE_PEER_MSPCONFIGPATH': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                  bcc_org_addr + os.sep + 'users' + os.sep +
                                                  bcc_admin_addr + os.sep + 'msp',
                       'CORE_PEER_ADDRESS': bcc_conn_addr + ':' + bcc_peer_port,
                       'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIG_REPO}

        script_manager.add(['peer', 'channel', 'create',
                            '-o', bcc_conn_addr + ':' + bcc_orderer_port,
                            '--ordererTLSHostnameOverride', bcc_orderer_addr,
                            '-c', channel_id,
                            '-f', './channel-artifacts/' + channel_id + '.tx',
                            '--outputBlock', './channel-artifacts/' + channel_id + '.block',
                            '--tls', 'true',
                            '--cafile', bcc_orderer_ca],
                           directory=ConfigRepo.NETWORK_NAME,
                           environment=environment)

        # ---- Join Channels ----

        for node in bcc_org_list:
            bcc_org_addr = node['addr']
            bcc_org_name = node['name']
            bcc_peer_addr = bcc_peer_dict[bcc_org_addr][0]['addr']
            ports = cls._read_and_strip_(bcc_peer_dict[bcc_org_addr][0]['ports']).split(';')
            bcc_peer_port = ports[0].strip()
            bcc_admin_addr = UserManager.find_first_admin_user(bcc_org_addr)

            environment = {'CORE_PEER_TLS_ENABLED': 'true',
                           'CORE_PEER_LOCALMSPID': bcc_org_name + 'MSP',
                           'CORE_PEER_TLS_ROOTCERT_FILE': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                          bcc_org_addr + os.sep + 'peers' + os.sep +
                                                          bcc_peer_addr + '/tls/ca.crt',
                           'CORE_PEER_MSPCONFIGPATH': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                      bcc_org_addr + os.sep + 'users' + os.sep +
                                                      bcc_admin_addr + os.sep + 'msp',
                           'CORE_PEER_ADDRESS': bcc_conn_addr + ':' + bcc_peer_port,
                           'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIG_REPO}

            # --- join channel ---
            script_manager.add(['peer', 'channel', 'join',
                                '-b', './channel-artifacts/' + channel_id + '.block'],
                               directory=ConfigRepo.NETWORK_NAME,
                               environment=environment)

        # ---- Update Anchor Peers ----

        for node in bcc_org_list:
            bcc_org_addr = node['addr']
            bcc_org_name = node['name']
            bcc_peer_addr = bcc_peer_dict[bcc_org_addr][0]['addr']
            ports = cls._read_and_strip_(bcc_peer_dict[bcc_org_addr][0]['ports']).split(';')
            bcc_peer_port = ports[0].strip()
            bcc_admin_addr = UserManager.find_first_admin_user(bcc_org_addr)

            environment = {'CORE_PEER_TLS_ENABLED': 'true',
                           'CORE_PEER_LOCALMSPID': bcc_org_name + 'MSP',
                           'CORE_PEER_TLS_ROOTCERT_FILE': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                          bcc_org_addr + os.sep + 'peers' + os.sep +
                                                          bcc_peer_addr + '/tls/ca.crt',
                           'CORE_PEER_MSPCONFIGPATH': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                      bcc_org_addr + os.sep + 'users' + os.sep +
                                                      bcc_admin_addr + os.sep + 'msp',
                           'CORE_PEER_ADDRESS': bcc_conn_addr + ':' + bcc_peer_port,
                           'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIG_REPO}

            # --- join channel ---
            script_manager.add(['peer', 'channel', 'update',
                                '-o', bcc_conn_addr + ':' + bcc_orderer_port,
                                '--ordererTLSHostnameOverride', bcc_orderer_addr,
                                '-c', channel_id,
                                '-f', './channel-artifacts/' + bcc_org_name + 'MSPanchors.tx',
                                '--tls', 'true',
                                '--cafile', bcc_orderer_ca],
                               directory=ConfigRepo.NETWORK_NAME,
                               environment=environment)

        # create the channel directory
        os.mkdir(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + channel_id)

        return None, component_dict, script_manager.serialize()

    @classmethod
    def join_channel(cls, component_manager, channel_id='mychannel'):

        component_dict = component_manager.get_clear_node_list()
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = DeployManager._get_lists_of_nodes_(component_dict)
        script_manager = ScriptManager()

        bcc_consortium_addr = cls._read_and_strip_(bcc_consortium_node['addr'])
        bcc_orderer_addr = cls._read_and_strip_(bcc_orderer_list[0]['addr'])  # FIX_ME: Multiple Orderer ???
        bcc_orderer_port = cls._read_and_strip_(bcc_orderer_list[0]['ports'])
        bcc_orderer_tlsca_cert = \
            '/opt/gopath/src/github.com/hyperledger/fabric/peer/organizations/ordererOrganizations/' + \
            bcc_consortium_addr + '/orderers/' + bcc_orderer_addr + '/msp/tlscacerts/tlsca.' + \
            bcc_consortium_addr + '-cert.pem'

        for org_node in bcc_org_list:
            bcc_org_addr = cls._read_and_strip_(org_node['addr'])
            bcc_org_name = cls._read_and_strip_(org_node['name'])
            for node in bcc_peer_dict[cls._read_and_strip_(org_node['addr'])]:
                bcc_peer_addr = cls._read_and_strip_(node['addr'])
                bcc_peer_port = cls._read_and_strip_(node['ports']).split(';')[0]
                bcc_admin_addr = UserManager.find_first_admin_user(bcc_org_addr)

                # Fetching the most recent configuration block for the channel

                environment = {'CORE_PEER_TLS_ENABLED': 'true',
                               'CORE_PEER_LOCALMSPID': bcc_org_name + 'MSP',
                               'CORE_PEER_TLS_ROOTCERT_FILE': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                              bcc_org_addr + os.sep + 'peers' + os.sep +
                                                              bcc_peer_addr + '/tls/ca.crt',
                               'CORE_PEER_MSPCONFIGPATH': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                          bcc_org_addr + os.sep + 'users' + os.sep +
                                                          bcc_admin_addr + os.sep + 'msp',
                               'CORE_PEER_ADDRESS': bcc_peer_addr + ':' + bcc_peer_port,
                               'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIG_REPO}

                script_manager.add(['docker', 'exec', 'cli.' + bcc_peer_addr,
                                    'peer', 'channel', 'fetch', '0',
                                    channel_id + '.block',
                                    '-o', bcc_orderer_addr + ':' + bcc_orderer_port,
                                    '--ordererTLSHostnameOverride', bcc_orderer_addr,
                                    '-c', channel_id,
                                    '--tls',
                                    '--cafile', bcc_orderer_tlsca_cert],
                                   directory=ConfigRepo.NETWORK_NAME,
                                   environment=environment)

                script_manager.add(['docker', 'exec', 'cli.' + bcc_peer_addr,
                                    'peer', 'channel', 'join', '-b',
                                    channel_id + '.block'],
                                   directory=ConfigRepo.NETWORK_NAME,
                                   environment=environment)

        # create the channel directory
        os.mkdir(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + channel_id)

        return None, component_dict, script_manager.serialize()


    @classmethod
    def add_org_to_channel(cls, component_manager, channel_id, file_content):

        if not file_content:
            return "Invalid Organization Config", None, None

        try:
            orgs_dict = json.loads(file_content)
        except:
            return "Invalid Organization Config", None, None

        # FIX_ME: At this point, it shall be read
        cls.read_channel_configuration(component_manager, channel_id)

        working_dir = ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.CHANNEL_REPO + os.sep + channel_id

        # Open dict and add new org
        with open(working_dir + os.sep + 'config_block.json', 'rb') as f:
            block_dict = json.load(f)

        # FIX_ME: Take the latest ??? [0]
        original_config_dict = block_dict['data']['data'][0]['payload']['data']['config']
        with open(working_dir + os.sep + 'original_config.json', 'w') as f:
            json.dump(original_config_dict, f)

        modified_config_dict = original_config_dict.copy()

        for elem in orgs_dict:
            print(elem)
            modified_config_dict['channel_group']['groups']['Application']['groups'][elem] = orgs_dict[elem]

        with open(working_dir + os.sep + 'modified_config.json', 'w') as f:
            json.dump(modified_config_dict, f)

        noerror, str_out, str_err = ScriptManager._execute_(
            ['configtxlator', 'proto_encode', '--input', 'original_config.json', '--type', 'common.Config',
             '--output', 'original_config.pb'], directory=working_dir)
        if noerror != 0:
            raise Exception(str_err.decode('utf-8'))

        noerror, str_out, str_err = ScriptManager._execute_(
            ['configtxlator', 'proto_encode', '--input', 'modified_config.json', '--type', 'common.Config',
             '--output', 'modified_config.pb'], directory=working_dir)
        if noerror != 0:
            raise Exception(str_err.decode('utf-8'))

        noerror, str_out, str_err = ScriptManager._execute_(
            ['configtxlator', 'compute_update', '--channel_id', channel_id, '--original', 'original_config.pb',
             '--updated', 'modified_config.pb', '--output', 'config_update.pb'], directory=working_dir)
        if noerror != 0:
            raise Exception(str_err.decode('utf-8'))

        noerror, str_out, str_err = ScriptManager._execute_(
            ['configtxlator', 'proto_decode', '--input', 'config_update.pb', '--type', 'common.ConfigUpdate',
             '--output', 'config_update.json'], directory=working_dir)
        if noerror != 0:
            raise Exception(str_err.decode('utf-8'))

        with open(working_dir + os.sep + 'config_update.json', 'rb') as f:
            config_update_dict = json.load(f)

        config_update_in_envelope_dict = {'payload':{'header':{'channel_header':{'channel_id':channel_id, "type":2}},
                                          'data':{'config_update': config_update_dict }}}

        with open(working_dir + os.sep + 'config_update_in_envelope.json', 'w') as f:
            json.dump(config_update_in_envelope_dict, f)

        noerror, str_out, str_err = ScriptManager._execute_(
            ['configtxlator', 'proto_encode', '--input', 'config_update_in_envelope.json', '--type', 'common.Envelope',
             '--output', 'config_update_in_envelope.pb'], directory=working_dir)
        if noerror != 0:
            raise Exception(str_err.decode('utf-8'))

        # --------------------------------
        #     Build Script to Execute
        # --------------------------------

        component_dict = component_manager.get_clear_node_list()
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = DeployManager._get_lists_of_nodes_(component_dict)

        script_manager = ScriptManager()

        # --- Sign TX ---

        # FIX_ME
        bcc_conn_addr = 'localhost'
        bcc_consortium_addr = bcc_consortium_node['addr']
        bcc_orderer_addr = bcc_orderer_list[0]['addr']
        bcc_orderer_port = bcc_orderer_list[0]['ports']

        # Use a stand alone peer to create the transaction
        # Configuration of the peer (core.yaml) is in ConfigRepo.CONFIG_REPO
        bcc_orderer_ca = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + \
                         bcc_consortium_addr + os.sep + 'orderers' + os.sep + bcc_orderer_addr + \
                         os.sep + 'msp/tlscacerts/tlsca.' + bcc_consortium_addr + '-cert.pem'

        for org_node in bcc_org_list:
            bcc_org_addr = cls._read_and_strip_(org_node['addr'])
            bcc_org_name = cls._read_and_strip_(org_node['name'])
            for node in bcc_peer_dict[bcc_org_addr]:
                bcc_peer_addr = node['addr']
                ports = cls._read_and_strip_(node['ports']).split(';')
                bcc_peer_port = ports[0].strip()
                bcc_admin_addr = UserManager.find_first_admin_user(bcc_org_addr)

                environment = {'CORE_PEER_TLS_ENABLED': 'true',
                               'CORE_PEER_LOCALMSPID': bcc_org_name + 'MSP',
                               'CORE_PEER_TLS_ROOTCERT_FILE': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                              bcc_org_addr + os.sep + 'peers' + os.sep +
                                                              bcc_peer_addr + '/tls/ca.crt',
                               'CORE_PEER_MSPCONFIGPATH': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep +
                                                          bcc_org_addr + os.sep + 'users' + os.sep +
                                                          bcc_admin_addr + os.sep + 'msp',
                               'CORE_PEER_ADDRESS': bcc_conn_addr + ':' + bcc_peer_port,
                               'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIG_REPO}

                script_manager.add(['peer', 'channel', 'signconfigtx', '-f',
                                    ConfigRepo.CHANNEL_REPO + os.sep + channel_id + os.sep + 'config_update_in_envelope.pb'],
                                   directory=ConfigRepo.NETWORK_NAME,
                                   environment=environment)


                script_manager.add(['peer', 'channel', 'update',
                                    '-o', bcc_conn_addr + ':' + bcc_orderer_port,
                                    '--ordererTLSHostnameOverride', bcc_orderer_addr,
                                    '-c', channel_id,
                                    '-f', ConfigRepo.CHANNEL_REPO + os.sep + channel_id + os.sep + 'config_update_in_envelope.pb',
                                    '--tls', 'true',
                                    '--cafile', bcc_orderer_ca],
                                   directory=ConfigRepo.NETWORK_NAME,
                                   environment=environment)

        return None, component_dict, script_manager.serialize()


    #  "========= Config transaction to add org3 to network created ===== "

    # 'peer channel signconfigtx -f "org3_update_in_envelope.pb"'

