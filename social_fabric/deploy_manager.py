#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
from glob import glob
from shutil import copyfile
from social_fabric.config_repo import ConfigRepo
from social_fabric.user_manager import UserManager
from social_fabric.owner_manager import OwnerManager
from social_fabric.script_manager import ScriptManager
from social_fabric.console_processor import ConsoleProcessor
from social_fabric.network_template_processor import NetworkTemplateProcessor
from social_fabric.password_manager import PasswordManager

def read_and_strip(str):
    if str:
        return str.strip()
    return None


class DeployManager:

    # -----------------------------------------------------------------
    #                   Deploy and Activate Methods
    # -----------------------------------------------------------------

    IMAGE_TAG = 'latest'    # FIX_ME shall follow fixed release as per packaged
    COMPOSE_PROJECT_NAME = 'net'  # FIX_ME What the hell is that!

    @staticmethod
    def _find_ports_(component_dict, owner_addr):
        for node in component_dict['nodes']:
            if node['owner']  == owner_addr:
                return node['ports']
        return ''

    @classmethod
    def _get_list_of_fabric_ca_(cls, component_dict):
        fabric_ca_list = component_dict['owners']
        for fabric_ca in fabric_ca_list:
            fabric_ca['port'] = cls._find_ports_(component_dict, fabric_ca['addr'])
        return component_dict['owners']

    @classmethod
    def _find_owner_(cls, component_dict, ca_addr):
        owner_list = cls._get_list_of_fabric_ca_(component_dict)
        for owner in owner_list:
            if owner['addr'] == ca_addr:
                return owner
        raise Exception('owner addr ' + ca_addr + ' not found')

    @staticmethod
    def _get_lists_of_nodes_(component_dict):
        bcc_consortium_node = None
        bcc_orderer_list = []
        bcc_org_list = []
        bcc_peer_dict = {}

        for node in component_dict['nodes']:
            node_type = node['type']
            if  node_type == 'consortium':
                bcc_consortium_node = node
            elif node_type == 'orderer':
                bcc_orderer_list.append(node)
            elif node_type == 'organization':
                org_addr = node['addr']
                bcc_org_list.append(node)
                bcc_peer_dict[org_addr] = []
            elif node_type == 'peer':
                bcc_peer_dict[org_addr].append(node)

        return bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict

    @classmethod
    def _validate_deploy_(cls, component_dict, working_mode):

        bcc_network_domain = read_and_strip(component_dict['addr'])
        if not bcc_network_domain:
            return "Consortium Domain Address is Mandatory"

        for elem in component_dict['owners']:
            bcc_ca_addr = read_and_strip(elem['addr'])
            if not bcc_ca_addr:
                return "Owner Address is Mandatory"
            bcc_ca_org = read_and_strip(elem['org'])
            if not bcc_ca_org:
                return "Owner organizarion for " + bcc_ca_addr + " is Mandatory"
            bcc_ca_password = read_and_strip(elem['password'])
            if not bcc_ca_password:
                return "Owner " + bcc_ca_addr + " must have a password"

        if working_mode == 'CreateNetwork':
            for node in component_dict['nodes']:
                node_type = node['type']
                if  node_type == 'consortium':
                    bcc_consortium_domain = read_and_strip(node['addr'])
                    if not bcc_consortium_domain:
                        return "Consortium Domain Address is Mandatory"
                    bcc_consortium_name = read_and_strip(node['name'])
                    if not bcc_consortium_name:
                        return "Consortium Name is Mandatory"
                    has_admin = False
                    user_list = UserManager.find_all_users(bcc_consortium_domain)
                    for user in user_list:
                        user_dict = UserManager.get_user_dict(bcc_consortium_domain, user)
                        if not user_dict['addr']:
                            return "Address is Mandatory for user " + user
                        if not user_dict['name']:
                            return "Name is Mandatory for user " + user
                        if not user_dict['password']:
                            return "Password is Mandatory for user " + user
                        if user_dict['name'] == 'admin':
                            return "Name 'admin' is not allowed for user " + user
                        if user_dict['admin']:
                            has_admin = True
                        if not has_admin:
                            return "Consortium {} must have at leasr one user with administrative rights".format(
                                bcc_consortium_domain)
                elif  node_type == 'orderer':
                    bcc_orderer_addr = read_and_strip(node['addr'])
                    if not bcc_orderer_addr:
                        return "Orderer Address is Mandatory"
                    bcc_orderer_name = read_and_strip(node['name'])
                    if not bcc_orderer_name:
                        return "Orderer Node " + bcc_orderer_addr + " must have a name"
                    bcc_orderer_password = read_and_strip(node['password'])
                    if not bcc_orderer_password:
                        return "Orderer Node " + bcc_orderer_addr + " must have a password"

        for node in component_dict['nodes']:
            node_type = node['type']
            if node_type == 'organization':
                bcc_org_addr = read_and_strip(node['addr'])
                if not bcc_org_addr:
                    return "Organization Address is Mandatory"
                if not read_and_strip(node['name']):
                    return "Organization Name for {} is Mandatory".format(bcc_org_addr)
                if not read_and_strip(node['ports']):
                    return "Organization port for {} is Mandatory".format(bcc_org_addr)
                has_admin = False
                user_list = UserManager.find_all_users(bcc_org_addr)
                for user in user_list:
                    user_dict = UserManager.get_user_dict(bcc_org_addr, user)
                    if not user_dict['addr']:
                        return "Address is Mandatory for user " + user
                    if not user_dict['name']:
                        return "Name is Mandatory for user " + user
                    if not user_dict['password']:
                        return "Password is Mandatory for user " + user
                    if user_dict['name'] == 'admin':
                        return "Name 'admin' is not allowed for user " + user
                    if user_dict['admin']:
                        has_admin = True
                if not has_admin:
                    return "Organization {} must have at leasr one user with administrative rights".format(bcc_org_addr)
            elif node_type == 'peer':
                bcc_peer_addr = read_and_strip(node['addr'])
                if not bcc_peer_addr:
                    return "Perr Address is Mandatory"
                bcc_peer_name = read_and_strip(node['name'])
                if not bcc_peer_name:
                    return "Peer Node " + bcc_peer_addr + " must have a name"
                ports = read_and_strip(node['ports']).split(';')
                if len(ports) < 2:
                    return "Peer Node " + bcc_peer_addr + " must have two set of ports separated by a semi-column"
                bcc_org_password = read_and_strip(node['password'])
                if not bcc_org_password:
                    return "Peer Node " + bcc_peer_addr + " must have a password"
        return None

    @classmethod
    def _generate_configtx_scripts_(cls, component_dict):

        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = cls._get_lists_of_nodes_(component_dict)

        net_template_processor = NetworkTemplateProcessor()

        output = net_template_processor.process('configtx.yaml', BCC_CONSORTIUM_ADDR=bcc_consortium_node['addr'],
                                                                 BCC_ORDERER_LIST=bcc_orderer_list,
                                                                 BCC_ORG_LIST=bcc_org_list,
                                                                 BCC_PEER_DICT=bcc_peer_dict)

        os.makedirs(ConfigRepo.CONFIGTX_REPO, exist_ok=True)
        with open(ConfigRepo.CONFIGTX_REPO + os.sep + 'configtx.yaml', 'w') as f:
            f.write(output)

    @classmethod
    def _generate_fabric_ca_scripts_(cls, component_dict):

        bcc_fabric_ca_list = cls._get_list_of_fabric_ca_(component_dict)

        net_template_processor = NetworkTemplateProcessor()

        for elem in bcc_fabric_ca_list:
            bcc_fabric_ca_addr = read_and_strip(elem['addr'])
            bcc_fabric_ca_organization = read_and_strip(elem['org'])
            bcc_fabric_ca_country = read_and_strip(elem['country'])
            bcc_fabric_ca_state = read_and_strip(elem['state'])
            bcc_fabric_ca_locality = read_and_strip(elem['locality'])
            bcc_fabric_ca_port = read_and_strip(elem['port'])
            bcc_fabric_ca_admin = 'admin' # FIX_ME
            bcc_fabric_ca_password = PasswordManager.decrypt(elem['password'])
            # Instantiate only if used
            if bcc_fabric_ca_port:
                output = net_template_processor.process('fabric-ca-server-config.yaml',
                                                         BCC_FABRIC_CA_NAME=bcc_fabric_ca_organization,
                                                         BCC_FABRIC_CA_ADMIN=bcc_fabric_ca_admin,
                                                         BCC_FABRIC_CA_PASSWORD=bcc_fabric_ca_password,
                                                         BCC_FABRIC_CA_ADDR=bcc_fabric_ca_addr,
                                                         BCC_FABRIC_CA_PORT=bcc_fabric_ca_port,
                                                         BCC_FABRIC_CA_ORGANIZATION=bcc_fabric_ca_organization,
                                                         BCC_FABRIC_CA_COUNTRY=bcc_fabric_ca_country,
                                                         BCC_FABRIC_CA_STATE=bcc_fabric_ca_state,
                                                         BCC_FABRIC_CA_LOCALITY=bcc_fabric_ca_locality)
                target_dir = ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + bcc_fabric_ca_addr
                os.makedirs(target_dir, exist_ok=True)
                with open(target_dir + os.sep + 'fabric-ca-server-config.yaml', 'w') as f:
                    f.write(output)

    @classmethod
    def _generate_docker_compose_scripts_(cls, component_dict, working_mode):

        net_template_processor = NetworkTemplateProcessor()

        bcc_user_id = str(os.getuid()) + ':' + str(os.getgid())
        bcc_fabric_ca_list = cls._get_list_of_fabric_ca_(component_dict)
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = cls._get_lists_of_nodes_(component_dict)

        bcc_consortium_addr = read_and_strip(bcc_consortium_node['addr'])

        bcc_peer_list = []
        for org in bcc_org_list:
            bcc_peer_list += bcc_peer_dict[org['addr']]
        output = net_template_processor.process('docker-compose-prefix.yaml',
                                                BCC_NETWORK_DOMAIN=bcc_consortium_addr,
                                                BCC_ORDERER_LIST=bcc_orderer_list,
                                                BCC_PEER_LIST=bcc_peer_list)

        for elem in bcc_fabric_ca_list:
            bcc_ca_addr = read_and_strip(elem['addr'])
            bcc_ca_public_cert = bcc_ca_addr + OwnerManager.CERT_SUFFIX
            bcc_ca_private_key = bcc_ca_addr + OwnerManager.KEY_SUFFIX
            bcc_ca_admin_name = 'admin' # FIX_ME
            bcc_ca_admin_password = PasswordManager.decrypt(elem['password'])
            bcc_ca_port = read_and_strip(elem['port'])
            # Instantiate only if used
            if bcc_ca_port:
                output += net_template_processor.process('docker-compose-ca.yaml',
                                                         BCC_USER_ID=bcc_user_id,
                                                         BCC_NETWORK_DOMAIN=bcc_consortium_addr,
                                                         BCC_CA_ADDR=bcc_ca_addr,
                                                         BCC_CA_PORT=bcc_ca_port,
                                                         BCC_CA_PUBLIC_CERT=bcc_ca_public_cert,
                                                         BCC_CA_PRIVATE_KEY=bcc_ca_private_key,
                                                         BCC_CA_ADMIN_NAME=bcc_ca_admin_name,
                                                         BCC_CA_ADMIN_PASSWORD=bcc_ca_admin_password)

        # --- Orderers ---
        if working_mode == 'CreateNetwork':
            for node in bcc_orderer_list:
                bcc_orderer_addr = read_and_strip(node['addr'])
                bcc_orderer_name = read_and_strip(node['name'])
                bcc_orderer_port = read_and_strip(node['ports'])
                output += net_template_processor.process('docker-compose-orderer.yaml',
                                                         BCC_NETWORK_DOMAIN=bcc_consortium_addr,
                                                         BCC_ORDERER_NAME=bcc_orderer_name,
                                                         BCC_ORDERER_ADDR=bcc_orderer_addr,
                                                         BCC_ORDERER_PORT=bcc_orderer_port)

        for org_node in bcc_org_list:
            bcc_org_addr = read_and_strip(org_node['addr'])
            bcc_org_name = read_and_strip(org_node['name'])
            for node in bcc_peer_dict[bcc_org_addr]:
                bcc_peer_addr = read_and_strip(node['addr'])
                bcc_couchdb_addr = 'couchdb.' + bcc_peer_addr
                ports = read_and_strip(node['ports']).split(';')
                bcc_peer_port = ports[0].strip()
                bcc_couchdb_port = ports[1].strip()
                bcc_org_admin_user_addr = None
                user_list = UserManager.find_all_users(bcc_org_addr)
                for user in user_list:
                    user_dict = UserManager.get_user_dict(bcc_org_addr, user)
                    if user_dict['admin']:
                        bcc_org_admin_user_addr = user
                bcc_cli_addr = 'cli.' + bcc_peer_addr
                output += net_template_processor.process('docker-compose-couchdb.yaml',
                                                         BCC_NETWORK_DOMAIN=bcc_consortium_addr,
                                                         BCC_COUCHDB_ADDR=bcc_couchdb_addr,
                                                         BCC_COUCHDB_PORT=bcc_couchdb_port)
                output += net_template_processor.process('docker-compose-peer.yaml',
                                                         BCC_NETWORK_DOMAIN=bcc_consortium_addr,
                                                         BCC_ORG_ADDR=bcc_org_addr,
                                                         BCC_ORG_NAME=bcc_org_name,
                                                         BCC_PEER_ADDR=bcc_peer_addr,
                                                         BCC_PEER_PORT=bcc_peer_port,
                                                         BCC_COUCHDB_ADDR=bcc_couchdb_addr,
                                                         BCC_COUCHDB_PORT=bcc_couchdb_port)
                output += net_template_processor.process('docker-compose-cli.yaml',
                                                         BCC_NETWORK_DOMAIN=bcc_consortium_addr,
                                                         BCC_ORG_ADDR=bcc_org_addr,
                                                         BCC_ORG_NAME=bcc_org_name,
                                                         BCC_PEER_ADDR=bcc_peer_addr,
                                                         BCC_PEER_PORT=bcc_peer_port,
                                                         BCC_CLI_ADDR=bcc_cli_addr,
                                                         BCC_ORG_ADMIN_USER_ADDR=bcc_org_admin_user_addr)

        os.makedirs(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.DOCKER_REPO, exist_ok=True)
        with open(ConfigRepo.NETWORK_NAME + os.sep + ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'w') as f:
            f.write(output)

    @staticmethod
    def _enroll_and_register_elem_(script_manager, org_node, target_type, target_node):

        ca_addr = org_node['owner']
        ca_name = org_node['owner']
        ca_port = org_node['ports']
        org_addr = org_node['addr']
        org_type = org_node['type']
        target_addr = target_node['addr']
        target_name = target_node['name']
        target_passwd = PasswordManager.decrypt(target_node['password'])
        conn = 'localhost'  # FIX_ME
        target_cert = conn + '-' + ca_port + '-' + ca_addr.replace('.', '-') + '.pem'
        target_tls_cert = 'tls-' + target_cert

        if org_type == 'consortium':
            environment = {'FABRIC_CA_CLIENT_HOME': os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + org_addr}
        else:
            environment = {'FABRIC_CA_CLIENT_HOME': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr}
        ca_tls_cert = os.getcwd() + os.sep + ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + ca_addr + os.sep + 'tls-cert.pem'

        # --- Register element ---
        script_manager.add(['fabric-ca-client', 'register', '--caname', ca_name,
                            '--id.name', target_name, '--id.secret', target_passwd, '--id.type', target_type,
                            '--tls.certfiles', ca_tls_cert],
                           directory=ConfigRepo.NETWORK_NAME,
                           environment=environment)

        # ---- Generate certificates
        url = 'https://' + target_name + ':' + target_passwd + '@' + conn + ':' + ca_port

        if target_type == 'peer':
            target_dir = os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr + os.sep + 'peers' + os.sep + target_addr
        elif target_type == 'orderer':
            target_dir = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + org_addr + os.sep + 'orderers' + os.sep + target_addr
        elif target_type in ('client', 'admin'):
            if org_type == 'consortium':
                target_dir = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + org_addr + os.sep + 'users' + os.sep + target_addr
            else:
                target_dir = os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr + os.sep + 'users' + os.sep + target_addr
        else:
            raise Exception("Unknown type " + target_type)

        # --- Generate MSP Certificate and key ---
        script_manager.add(['fabric-ca-client', 'enroll', '-u', url, '--caname', ca_name, '-M', target_dir + os.sep + 'msp',
                            '--tls.certfiles', ca_tls_cert],
                           directory=ConfigRepo.NETWORK_NAME,
                           environment=environment)

        # --- Copy and rename certificate
        if target_type in ('peer', 'orderer'):
            if target_type == 'orderer':
                dest_dir = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + org_addr + os.sep + 'ca'
            else:
                dest_dir = os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr + os.sep + 'ca'
            script_manager.add(['mkdir', '-p', dest_dir],
                               directory=ConfigRepo.NETWORK_NAME,
                               environment=environment)
            script_manager.add(['cp', target_dir + os.sep + 'msp' + os.sep + 'cacerts' + os.sep + target_cert,
                                dest_dir + os.sep + 'ca.' + org_addr + '-cert.pem'],
                               directory=ConfigRepo.NETWORK_NAME,
                               environment=environment)

        # --- Generate TLS Certificate and key ---
        if target_type in ('orderer', 'peer'):
            script_manager.add(['fabric-ca-client', 'enroll', '-u', url, '--caname', ca_name,
                                '-M', target_dir + os.sep + 'tls',
                                '--enrollment.profile', 'tls',
                                '--csr.hosts', target_addr, '--csr.hosts', conn,
                                '--tls.certfiles', ca_tls_cert],
                               directory=ConfigRepo.NETWORK_NAME,
                               environment=environment)

            # Copy and rename certificates
            script_manager.add(['cp', target_dir + os.sep + 'tls' + os.sep + 'tlscacerts' + os.sep + target_tls_cert,
                                      target_dir + os.sep + 'tls' + os.sep + 'ca.crt'],
                               directory = ConfigRepo.NETWORK_NAME,
                               environment = environment)
            script_manager.add(['cp', target_dir + os.sep + 'tls' + os.sep + 'signcerts' + os.sep + 'cert.pem',
                                      target_dir + os.sep + 'tls' + os.sep + 'server.crt'],
                               directory = ConfigRepo.NETWORK_NAME,
                               environment = environment)
            #script_manager.add(['echo', '"cp ' + target_dir + os.sep + 'tls' + os.sep + 'keystore' + os.sep + '* ' +
            #                    target_dir + os.sep + 'tls' + os.sep + 'server.key"', '|', 'bash'],
            #                   directory = ConfigRepo.NETWORK_NAME,
            #                   environment = environment)

            if target_type == 'orderer':
                dest_dir = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + org_addr + os.sep + 'orderers' + os.sep + target_addr + os.sep + 'msp' + os.sep + 'tlscacerts'
                script_manager.add(['mkdir', '-p', dest_dir],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)
                script_manager.add(['cp', target_dir + os.sep + 'tls' + os.sep + 'tlscacerts' + os.sep + target_tls_cert,
                                          dest_dir + os.sep + 'tlsca.' + org_addr + '-cert.pem'],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)

                dest_dir = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + org_addr + os.sep + 'msp' + os.sep + 'tlscacerts'
                script_manager.add(['mkdir', '-p', dest_dir],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)
                script_manager.add(['cp', target_dir + os.sep + 'tls' + os.sep + 'tlscacerts' + os.sep + target_tls_cert,
                                          dest_dir + os.sep + 'tlsca.' + org_addr + '-cert.pem'],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)

            else:  # peer
                dest_dir = os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr + os.sep + 'msp' + os.sep + 'tlscacerts'
                script_manager.add(['mkdir', '-p', dest_dir],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)
                script_manager.add(['cp', target_dir + os.sep + 'tls' + os.sep + 'tlscacerts' + os.sep + target_tls_cert,
                                          dest_dir + os.sep + 'ca.crt'],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)

                dest_dir = os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr + os.sep + 'tlsca'
                script_manager.add(['mkdir', '-p', dest_dir],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)
                script_manager.add(['cp', target_dir + os.sep + 'tls' + os.sep + 'tlscacerts' + os.sep + target_tls_cert,
                                          dest_dir + os.sep + 'tlsca.' + org_addr + '-cert.pem'],
                                   directory = ConfigRepo.NETWORK_NAME,
                                   environment = environment)

    @classmethod
    def _enroll_and_register_users_(cls, script_manager, ca_node, node):
        org_addr = node['addr']
        user_list = UserManager.find_all_users(org_addr)
        for user in user_list:
            user_dict = UserManager.get_user_dict(org_addr, user)
            target_type = 'client'
            if user_dict['admin']:
                target_type = 'admin'
            cls._enroll_and_register_elem_(script_manager, node, target_type, user_dict)

    @staticmethod
    def _enroll_and_register_org_(script_manager, ca_node, node):

        # --- Generate Keys and certificates for (enroll) the CA admin ---
        org_addr = node['addr']  # 'org1.example.com'
        ca_addr = node['owner']  # 'ca.org1.example.com'
        ca_name = node['owner']  # FIX_ME  'ca.org1.example.com'
        ca_port = node['ports']  # '7052'
        username = 'admin'       # FIX_ME
        password = PasswordManager.decrypt(ca_node['password'])
        conn = 'localhost'

        ca_tls_cert = os.getcwd() + os.sep + ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + ca_addr + os.sep + 'tls-cert.pem'
        url = 'https://' + username + ':' + password + '@' + conn + ':' + ca_port
        environment = {'FABRIC_CA_CLIENT_HOME': os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr}
        script_manager.add(['fabric-ca-client', 'enroll', '-u', url, '--caname', ca_name, '--tls.certfiles', ca_tls_cert],
                           directory=ConfigRepo.NETWORK_NAME,
                           environment=environment)

    @staticmethod
    def _enroll_and_register_consortium_(script_manager, ca_node, node):

        # --- Generate Keys and certificates for (enroll) the CA admin ---
        consortium_addr = node['addr']  # 'example.com'
        ca_addr = node['owner']  # 'ca.example.com'
        ca_name = node['owner']  # FIX_ME 'ca.example.com'
        ca_port = node['ports']  # '7051'
        username = 'admin'
        password = PasswordManager.decrypt(ca_node['password'])
        conn = 'localhost'

        ca_tls_cert = os.getcwd() + os.sep + ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + ca_addr + os.sep + 'tls-cert.pem'
        url = 'https://' + username + ':' + password + '@' + conn + ':' + ca_port
        environment = {'FABRIC_CA_CLIENT_HOME': os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + consortium_addr}
        script_manager.add(['fabric-ca-client', 'enroll', '-u', url, '--caname', ca_name, '--tls.certfiles', ca_tls_cert],
                           directory=ConfigRepo.NETWORK_NAME,
                           environment=environment)

    @classmethod
    def _create_organization_tree_structure_(cls, component_dict, working_mode):

        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = cls._get_lists_of_nodes_(component_dict)

        # Consortium
        bcc_consortium_addr = read_and_strip(bcc_consortium_node['addr'])
        target_dir = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'msp'
        os.makedirs(target_dir, exist_ok=True)

        # Consortium Users
        user_list = UserManager.find_all_users(bcc_consortium_addr)
        for user in user_list:
            target_dir = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'users' + os.sep + user + os.sep + 'msp'
            os.makedirs(target_dir, exist_ok=True)

        # Orderer
        for node in bcc_orderer_list:
            bcc_orderer_addr = read_and_strip(node['addr'])
            orderer_dir = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'orderers' + os.sep + bcc_orderer_addr
            os.makedirs(orderer_dir, exist_ok=True)
            # Special case: copy the given certificate into the target deployment directory
            if working_mode == 'AttachOrganizations':
                os.makedirs(orderer_dir + os.sep + 'msp', exist_ok=True)
                os.makedirs(orderer_dir + os.sep + 'msp' + os.sep + 'tlscacerts', exist_ok=True)
                copyfile(ConfigRepo.ORDERER_SRC_REPO + os.sep + bcc_consortium_addr + os.sep + 'orderers' + os.sep +
                         bcc_orderer_addr + os.sep + 'msp' + os.sep + 'tlscacerts' + os.sep + 'tlsca.' + bcc_consortium_addr + '-cert.pem',
                         orderer_dir      + os.sep + 'msp' + os.sep + 'tlscacerts' + os.sep + 'tlsca.' + bcc_consortium_addr + '-cert.pem')
        for org_node in bcc_org_list:
            bcc_org_addr = read_and_strip(org_node['addr'])
            target_dir = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr
            os.makedirs(target_dir + os.sep + 'ca', exist_ok=True)
            os.makedirs(target_dir + os.sep + 'msp', exist_ok=True)
            os.makedirs(target_dir + os.sep + 'tlsca', exist_ok=True)

            # Users
            user_list = UserManager.find_all_users(bcc_org_addr)
            for user in user_list:
                target_dir = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'users' + os.sep + user + os.sep + 'msp'
                os.makedirs(target_dir, exist_ok=True)
            # Peers
            for node in bcc_peer_dict[bcc_org_addr]:
                bcc_peer_addr = read_and_strip(node['addr'])
                target_dir = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'peers' + os.sep + bcc_peer_addr
                os.makedirs(target_dir + os.sep + 'msp', exist_ok=True)
                os.makedirs(target_dir + os.sep + 'tls', exist_ok=True)

        # --- Create directories for blocks and channels
        os.makedirs(ConfigRepo.NETWORK_NAME + os.sep + 'channel-artifacts', exist_ok=True)
        os.makedirs(ConfigRepo.NETWORK_NAME + os.sep + 'system-genesis-block', exist_ok=True)

    @classmethod
    def _generate_deployment_script_(cls, component_dict, working_mode):

        script_manager = ScriptManager()

        bcc_fabric_ca_list = cls._get_list_of_fabric_ca_(component_dict)
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = cls._get_lists_of_nodes_(component_dict)

        # ---- Start Fabric CA Services ----
        for node in bcc_fabric_ca_list:
            if node['port']:
                ca_addr = read_and_strip(node['addr'])
                script_manager.add(['docker-compose', '-f',
                                    ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'up', '-d', ca_addr],
                                   directory=ConfigRepo.NETWORK_NAME,
                                   environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                                'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        # ---- Pause ----
        script_manager.add(['sleep', '10'])

        # ---- Enroll and Register Admin and Users of Orgs ----
        for org_node in bcc_org_list:
            ca_node = cls._find_owner_(component_dict, read_and_strip(org_node['owner']))
            cls._enroll_and_register_org_(script_manager, ca_node, org_node)
            cls._enroll_and_register_users_(script_manager, ca_node, org_node)
            for node in bcc_peer_dict[read_and_strip(org_node['addr'])]:
                cls._enroll_and_register_elem_(script_manager, org_node, 'peer', node)

        # ---- Enroll and Register Admin and Users of Consortium (Orderers) ----
        if working_mode == 'CreateNetwork':
            ca_node = cls._find_owner_(component_dict, read_and_strip(bcc_consortium_node['owner']))
            cls._enroll_and_register_consortium_(script_manager, ca_node, bcc_consortium_node)
            cls._enroll_and_register_users_(script_manager, ca_node, bcc_consortium_node)
            for node in bcc_orderer_list:
                cls._enroll_and_register_elem_(script_manager, bcc_consortium_node, 'orderer', node)

        # ---- Key dependant file generation ----

        script_manager.add(['python', 'COPY_KEYS()'])

        script_manager.add(['python', 'CREATE_CONFIG_YAML()'])

        script_manager.add(['python', 'CREATE_CONNECTION_FILES()'])

        # ---- Create Genesis Block ----

        if working_mode == 'CreateNetwork':

            # FIX_ME: Single Orderer + create an initial system channel (unused?)
            script_manager.add(['configtxgen',
                                 '-profile', 'TwoOrgsOrdererGenesis',
                                 '-channelID', 'system-channel',                       # channel_id,
                                 '-outputBlock', './system-genesis-block/genesis.block'],
                                directory=ConfigRepo.NETWORK_NAME,
                                environment={'FABRIC_CFG_PATH': os.getcwd() + os.sep + ConfigRepo.CONFIGTX_REPO})

            # ---- Start Orderer and Nodes Services ----
            for node in bcc_orderer_list:
                name = node['addr']
                script_manager.add(['docker-compose', '-f',
                    ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'up', '-d', name],
                    directory=ConfigRepo.NETWORK_NAME,
                    environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                 'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        # --- start components ---
        for org_node in bcc_org_list:
            for node in bcc_peer_dict[read_and_strip(org_node['addr'])]:
                peer_name = node['addr']
                couchdb_name = 'couchdb.' + peer_name
                cli_name = 'cli.' + peer_name

                # FIX_ME CouchDB should be a different node
                script_manager.add(['docker-compose', '-f',
                    ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'up', '-d', couchdb_name, peer_name, cli_name],
                    directory = ConfigRepo.NETWORK_NAME,
                    environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                 'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        return None, component_dict, script_manager.serialize()

    # -----------------------------
    #      Deactivate
    # -----------------------------
    @classmethod
    def deactivate(cls, component_dict):

        script_manager = ScriptManager()
        script_manager.add(['docker-compose', '-f', ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'down'],
                            directory=ConfigRepo.NETWORK_NAME,
                            environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                         'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        return None, component_dict, script_manager.serialize()

    # -----------------------------
    #      Reactivate
    # -----------------------------
    @classmethod
    def reactivate(cls, component_manager):

        component_dict = component_manager.get_clear_node_list()
        working_mode, _ = ConfigRepo.load_working_conf()
        script_manager = ScriptManager()

        bcc_fabric_ca_list = cls._get_list_of_fabric_ca_(component_dict)
        bcc_consortium_node, bcc_orderer_list, bcc_org_list, bcc_peer_dict = cls._get_lists_of_nodes_(component_dict)

        # ---- Start Fabric CA Services ----
        for node in bcc_fabric_ca_list:
            if node['port']:
                ca_addr = read_and_strip(node['addr'])
                script_manager.add(['docker-compose', '-f',
                                    ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'up', '-d', ca_addr],
                                   directory=ConfigRepo.NETWORK_NAME,
                                   environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                                'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        if working_mode == 'CreateNetwork':

            # ---- Start Orderer and Nodes Services ----
            for node in bcc_orderer_list:
                name = node['addr']
                script_manager.add(['docker-compose', '-f',
                    ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'up', '-d', name],
                    directory=ConfigRepo.NETWORK_NAME,
                    environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                 'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        # --- start components ---
        for org_node in bcc_org_list:
            for node in bcc_peer_dict[read_and_strip(org_node['addr'])]:
                # FIX_ME CouchDB should be a different node
                peer_name = node['addr']
                couchdb_name = 'couchdb.' + peer_name
                cli_name = 'cli.' + peer_name
                script_manager.add(['docker-compose', '-f',
                    ConfigRepo.DOCKER_REPO + os.sep + 'docker-compose.yaml', 'up', '-d', couchdb_name, peer_name, cli_name],
                    directory = ConfigRepo.NETWORK_NAME,
                    environment={'IMAGE_TAG': cls.IMAGE_TAG,
                                 'COMPOSE_PROJECT_NAME': cls.COMPOSE_PROJECT_NAME})

        return None, component_dict, script_manager.serialize()

    # -----------------------------
    #      Deploy and Activate
    # -----------------------------
    @classmethod
    def deploy_activate(cls, component_manager):

        component_dict = component_manager.get_clear_node_list()
        working_mode, _ = ConfigRepo.load_working_conf()

        # ---- Don't deploy is one server is up, just activate ----
        for node in component_dict['nodes']:
            if node['status'] == 'active':
                return "Deployment not allowed if one server is active", None, None

        if os.path.exists(os.getcwd() + os.sep + ConfigRepo.TARGET_REPO):
            return "Target directory " + os.getcwd() + os.sep + ConfigRepo.TARGET_REPO + " already exists\n remove directory before deploying"

        # ---- Validation ----
        msg = cls._validate_deploy_(component_dict, working_mode)
        if msg:
            return msg, None, None

        # ---- Fabric CA Server Configuration (yaml) ----
        cls._generate_fabric_ca_scripts_(component_dict)

        # ---- Configtx Script Generation ----
        cls._generate_configtx_scripts_(component_dict)

        # ---- Docker Compose Script Generation ----
        cls._generate_docker_compose_scripts_(component_dict, working_mode)

        # ---- Create the tree structure of organizations ---
        cls._create_organization_tree_structure_(component_dict, working_mode)

        # -----------------------------------------------
        #             Build execute list
        # -----------------------------------------------
        return cls._generate_deployment_script_(component_dict, working_mode)

    # ------------------------------------------------------------------------------------
    #         Methods called during processing of the deployment script
    # ------------------------------------------------------------------------------------

    @classmethod
    def _copy_private_keys_(cls, component_dict):

        working_mode, _ = ConfigRepo.load_working_conf()
        consortium_node, orderer_list, org_list, peer_dict = cls._get_lists_of_nodes_(component_dict)

        if working_mode == 'CreateNetwork':
            consortium_addr = read_and_strip(consortium_node['addr'])
            for node in orderer_list:
                orderer_addr = node['addr']
                target_dir = os.getcwd() + os.sep + ConfigRepo.ORDERER_TARGET_REPO + os.sep + consortium_addr + os.sep + 'orderers' + os.sep + orderer_addr
                for filename in glob(target_dir + os.sep + 'tls' + os.sep + 'keystore/*'):
                    copyfile(filename, target_dir + os.sep + 'tls' + os.sep + 'server.key')

        for org_node in org_list:
            org_addr = read_and_strip(org_node['addr'])
            for node in peer_dict[org_addr]:
                peer_addr = node['addr']
                target_dir = os.getcwd() + os.sep + ConfigRepo.PEER_TARGET_REPO + os.sep + org_addr + os.sep + 'peers' + os.sep + peer_addr
                for filename in glob(target_dir + os.sep + 'tls' + os.sep + 'keystore/*'):
                    copyfile(filename, target_dir + os.sep + 'tls' + os.sep + 'server.key')

    @classmethod
    def _create_config_yaml_(cls, component_dict):

        net_template_processor = NetworkTemplateProcessor()

        working_mode, _ = ConfigRepo.load_working_conf()
        consortium_node, orderer_list, org_list, peer_dict = cls._get_lists_of_nodes_(component_dict)
        local_addr = 'localhost'  # FIX_ME

        if working_mode == 'CreateNetwork':
            # Consortium
            bcc_consortium_addr = read_and_strip(consortium_node['addr'])
            bcc_consortium_port = read_and_strip(consortium_node['ports'])
            bcc_ca_addr = read_and_strip(consortium_node['owner'])
            bcc_ca_cert = local_addr + '-' + bcc_consortium_port + '-' + bcc_ca_addr.replace('.', '-') + '.pem'
            target_dir = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'msp'
            with open(target_dir + os.sep + 'config.yaml', 'w') as f:
                f.write(net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=bcc_ca_cert))

            # Consortium Users
            user_list = UserManager.find_all_users(bcc_consortium_addr)
            for user in user_list:
                target_dir = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'users' + os.sep + user + os.sep + 'msp'
                user_dict = UserManager.get_user_dict(bcc_consortium_addr, user)
                if user_dict['admin']:
                    with open(target_dir + os.sep + 'config.yaml', 'w') as f:
                        f.write(net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=bcc_ca_cert))

            # Orderers
            for node in orderer_list:
                bcc_orderer_addr = read_and_strip(node['addr'])
                target_dir = ConfigRepo.ORDERER_TARGET_REPO + os.sep + bcc_consortium_addr + os.sep + 'orderers' + os.sep + bcc_orderer_addr + os.sep + 'msp'
                with open(target_dir + os.sep + 'config.yaml', 'w') as f:
                    f.write(net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=bcc_ca_cert))

        # Organizations
        for org_node in org_list:
            bcc_org_addr = read_and_strip(org_node['addr'])
            bcc_org_port = read_and_strip(org_node['ports'])
            bcc_ca_addr = read_and_strip(org_node['owner'])
            bcc_ca_cert = local_addr + '-' + bcc_org_port + '-' + bcc_ca_addr.replace('.', '-') + '.pem'
            target_dir = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'msp'
            with open(target_dir + os.sep + 'config.yaml', 'w') as f:
                f.write(net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=bcc_ca_cert))

            # Organization Users
            user_list = UserManager.find_all_users(bcc_org_addr)
            for user in user_list:
                target_dir = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'users' + os.sep + user + os.sep + 'msp'
                user_dict = UserManager.get_user_dict(bcc_org_addr, user)
                if user_dict['admin']:
                    with open(target_dir + os.sep + 'config.yaml', 'w') as f:
                        f.write(net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=bcc_ca_cert))

            # Organization Peers
            for node in peer_dict[bcc_org_addr]:
                bcc_peer_addr = read_and_strip(node['addr'])
                target_dir = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'peers' + os.sep + bcc_peer_addr + os.sep + 'msp'
                with open(target_dir + os.sep + 'config.yaml', 'w') as f:
                    f.write(net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=bcc_ca_cert))

    @classmethod
    def _create_connection_files_(cls, component_dict):

        bcc_conn_addr = 'localhost'  # FIX_ME
        net_template_processor = NetworkTemplateProcessor()

        _, _, org_list, peer_dict = cls._get_lists_of_nodes_(component_dict)

        # Organizations
        for org_node in org_list:
            bcc_org_addr = read_and_strip(org_node['addr'])
            bcc_org_name = read_and_strip(org_node['name'])
            bcc_org_port = read_and_strip(org_node['ports'])
            bcc_ca_addr = read_and_strip(org_node['owner'])
            bcc_ca_org = cls._find_owner_(component_dict, bcc_ca_addr)['org']

            # tlsca certificate
            tls_peer_cert_filename = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'tlsca' + \
                                     os.sep + 'tlsca.' + bcc_org_addr + '-cert.pem'
            with open(tls_peer_cert_filename, 'rt') as f:
                tls_peer_cert = f.read()
            # ca certificate
            tls_ca_cert_filename = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'ca' + \
                                   os.sep + bcc_ca_addr + '-cert.pem'
            with open(tls_ca_cert_filename, 'rt') as f:
                tls_ca_cert = f.read()

            # Organization's Peers
            for node in peer_dict[bcc_org_addr]:
                bcc_peer_addr = read_and_strip(node['addr'])
                bcc_peer_name = read_and_strip(node['name'])
                ports = read_and_strip(node['ports']).split(';')
                bcc_peer_port = ports[0].strip()
                filename = ConfigRepo.PEER_TARGET_REPO + os.sep + bcc_org_addr + os.sep + 'peers' + os.sep + \
                           bcc_peer_addr + os.sep + 'connection-' + bcc_peer_name + '.json'
                with open(filename, 'w') as f:
                    f.write(net_template_processor.process('connection.json',
                                                           BCC_NETWORK_NAME=ConfigRepo.NETWORK_NAME,
                                                           BCC_CONN_ADDR=bcc_conn_addr,
                                                           BCC_CA_ADDR=bcc_ca_addr,
                                                           BCC_CA_NAME=bcc_ca_org,
                                                           BCC_ORG_NAME=bcc_org_name,
                                                           BCC_ORG_PORT=bcc_org_port,
                                                           BCC_PEER_ADDR=bcc_peer_addr,
                                                           BCC_PEER_PORT=bcc_peer_port,
                                                           BCC_PEER_CERT=tls_peer_cert,
                                                           BCC_CA_CERT=tls_ca_cert))

    # -------------------------
    #     Deploy Method
    # -------------------------
    @classmethod
    def deploy(cls, component_dict, execute_list):

        script_manager = ScriptManager(execute_list)
        instruction = script_manager.next_instruction()
        if not instruction:
            return 'done', component_dict, script_manager.serialize()

        command = instruction['command']
        directory = instruction['directory']
        environment = instruction['environment']

        if (command[0] == 'python'):
            error_code = 0
            cmd = command[1]
            if cmd == 'COPY_KEYS()':
                cls._copy_private_keys_(component_dict)
            elif cmd == 'CREATE_CONFIG_YAML()':
                cls._create_config_yaml_(component_dict)
            elif cmd == 'CREATE_CONNECTION_FILES()':
                cls._create_connection_files_(component_dict)
            component_dict['errorcode'] = error_code
            component_dict['msg'] = '+ ' + cmd + '<br>'
        else:
            error_code, str_out, str_err = script_manager.execute(command,
                                                                 directory=directory,
                                                                 environment=environment)
            component_dict['errorcode'] = error_code
            component_dict['msg'] = ConsoleProcessor.convert(error_code, str_out + str_err)

        return None, component_dict, script_manager.serialize()

