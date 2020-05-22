#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import json
from shutil import rmtree, copyfile
from werkzeug.utils import secure_filename
#from social_fabric.cert_manager import CertManager
from social_fabric.config_repo import ConfigRepo
from social_fabric.network_template_processor import NetworkTemplateProcessor
from social_fabric.password_manager import PasswordManager

class OwnerManager:

    CERT_SUFFIX = '-cert.pem'
    KEY_SUFFIX = '-priv.key'

    def __init__(self):
        #self.cert_manager = CertManager()
        self.owner_list = []
        #self.build_owner_list()  FIX_ME

    @staticmethod
    def _save_owner_dict_(owner_dict, owner_path, owner):
        filename = owner_path + os.sep + owner + '.json'
        with open(filename, 'w') as f:
            json.dump(owner_dict, f)

    @staticmethod
    def _load_owner_dict_(owner_path, owner):
        filename = owner_path + os.sep + owner + '.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                user_dict = json.load(f)
        else:
            user_dict = {'org': '', 'country': 'CA', 'state': 'QC', 'locality': 'Montreal', 'addr': '',
                          'password': '', 'catype': '', 'caroot': ''}
            with open(filename, 'w') as f:
                json.dump(user_dict, f)
        return user_dict

    def build_owner_list(self, with_password=False):
        if not os.path.exists(ConfigRepo.FABIC_CA_SRC_REPO):
            os.makedirs(ConfigRepo.FABIC_CA_SRC_REPO)
        dir_list = os.listdir(ConfigRepo.FABIC_CA_SRC_REPO)
        self.owner_list = []
        for elem in dir_list:
            owner_dict = OwnerManager._load_owner_dict_(ConfigRepo.FABIC_CA_SRC_REPO + os.sep + elem, elem)
            if not with_password:
                if owner_dict['password']:
                    owner_dict['password'] = PasswordManager.DISPLAYED_PASS
            self.owner_list.append(owner_dict)
        return self.owner_list

    def add_owner(self, org, country, state, locality, addr, catype, caroot):
        self.owner_list.append({'org': org, 'country': country, 'state': state, 'locality': locality, 'addr': addr, 'password': '', 'catype': catype, 'caroot': caroot})
        return None, self.owner_list

    def delete_owner(self, addr):
        dir_list = os.listdir(ConfigRepo.FABIC_CA_SRC_REPO)
        for elem in dir_list:
            if elem == addr:
                try:
                    rmtree(ConfigRepo.FABIC_CA_SRC_REPO + os.sep + addr)
                except:
                    pass
                return None, self.build_owner_list()
        return 'organization ' + addr + ' not found', None

    def set_password(self, addr, password):
        owner_dict = OwnerManager._load_owner_dict_(ConfigRepo.FABIC_CA_SRC_REPO + os.sep + addr, addr)
        owner_dict['password'] = PasswordManager.encrypt(password)
        OwnerManager._save_owner_dict_(owner_dict, ConfigRepo.FABIC_CA_SRC_REPO + os.sep + addr, addr)

        return None, self.build_owner_list()

    # -----------------------------------------------------------
    #                   Target Generation
    # -----------------------------------------------------------

    # Generate a self signed owner certificate
    @staticmethod
    def gen_owner_cert(org, country, state, locality, addr):
        # Validate
        if not org:
            return 'Organization must have a value to generate a certificate', None
        if not addr:
            return 'DNS Domain must have a value to generate a certificate', None

        cert_dir = ConfigRepo.FABIC_CA_SRC_REPO + os.sep + addr
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)

        # Generate
        # cert_pem, key_pem = CertManager.gen_self_signed(org, country, state, locality, addr)

        # Write private key and certificate
        # with open(cert_dir + os.sep + addr + OwnerManager.CERT_SUFFIX, 'wb') as f:
        #     f.write(cert_pem)
        # with open(cert_dir + os.sep + addr + OwnerManager.KEY_SUFFIX, 'wb') as f:
        #     f.write(key_pem)

        owner_dict = {'org': org, 'addr': addr, 'password': '', 'country': country, 'state': state, 'locality': locality, 'catype': 'Self Signed', 'caroot': 'Internal'}
        with open(cert_dir + os.sep + addr + '.json', 'w') as f:
            f.write(json.dumps(owner_dict))

        return None, owner_dict

    @staticmethod
    def import_owner_cert(org, country, state, locality, addr, file):
        filename = secure_filename(file.filename)

        # FIX_ME
        file.save('/tmp/' + filename)
        subject_name, issuer_name, subject_country, subject_state, subject_locality = CertManager.cert_manager.read('/tmp/' + filename)

        if subject_country:
            country = subject_country
        if subject_state:
            state = subject_state
        if subject_locality:
            locality = subject_locality

        if subject_name == issuer_name:
            catype = 'Self Signed'
            caroot = 'Internal'
        else:
            catype = 'Externally Signed'
            caroot = issuer_name

        return None, {'org': org, 'country': country, 'state': state, 'locality': locality, 'addr': subject_name, 'catype': catype, 'caroot': caroot}

    def get_owner_list(self):
        return None, self.build_owner_list()

    def get_clear_owner_list(self):
        return None, self.build_owner_list(with_password=True)

    # ------------------------------------------------------
    #           Certificate Generation
    # ------------------------------------------------------

    @staticmethod
    def get_root_key_and_pem(owner_addr):
        cert_dir = ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + owner_addr
        return cert_dir + os.sep + owner_addr + OwnerManager.KEY_SUFFIX, cert_dir + os.sep + owner_addr + OwnerManager.CERT_SUFFIX

    @staticmethod
    def get_root_pem(owner_addr):
        cert_dir = ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + owner_addr
        return cert_dir + os.sep + owner_addr + OwnerManager.CERT_SUFFIX

    @staticmethod
    def gen_signed_cert(owner_addr, target_addr, purpose):
        cert_dir = ConfigRepo.FABIC_CA_TARGET_REPO + os.sep + owner_addr
        ca_key_filename = cert_dir + os.sep + owner_addr + OwnerManager.KEY_SUFFIX
        ca_cert_filename = cert_dir + os.sep + owner_addr + OwnerManager.CERT_SUFFIX
        return CertManager.gen_signed_cert(ca_key_filename, ca_cert_filename, target_addr, purpose)

    @staticmethod
    def copy_msp_admin_files(base_dir, user_dir=None):
        if not user_dir:
            user_dir = base_dir
        for user in os.listdir(user_dir + os.sep + 'users'):
            path = user_dir + os.sep + 'users' + os.sep + user + os.sep + 'msp' + os.sep + 'signcerts'
            file_list = os.listdir(path)
            for filename in file_list:
                # FIX_ME: Hack, shall be based on user profile
                if 'Admin' in filename:
                    admin_pem_filename = path + os.sep + filename
                    target_dir = base_dir + os.sep + 'msp' + os.sep + 'admincerts'
                    os.makedirs(target_dir, exist_ok=True)
                    copyfile(admin_pem_filename, target_dir + os.sep + file_list[0])

    @staticmethod
    def gen_msp_cert_files(root_name, root_pem_filename, base_dir, target_name, purpose):

        cert_pem, key_pem = OwnerManager.gen_signed_cert(root_name, target_name, purpose)

        rmtree(base_dir + os.sep + 'msp', ignore_errors=True)

        target_dir = base_dir + os.sep + 'msp' + os.sep + 'cacerts'
        os.makedirs(target_dir, exist_ok=True)
        copyfile(root_pem_filename, target_dir + os.sep + os.path.basename(root_pem_filename))

        net_template_processor = NetworkTemplateProcessor()
        output = net_template_processor.process('config.yaml', BCC_CA_PEM_CERT=os.path.basename(root_pem_filename))
        with open(base_dir + os.sep + 'msp' + os.sep + 'config.yaml', 'w') as f:
            f.write(output)

        target_dir = base_dir + os.sep + 'msp' + os.sep + 'keystore'
        os.makedirs(target_dir, exist_ok=True)
        with open(target_dir + os.sep + target_name + OwnerManager.KEY_SUFFIX, 'wb') as f:
            f.write(key_pem)

        target_dir = base_dir + os.sep + 'msp' + os.sep + 'signcerts'
        os.makedirs(target_dir, exist_ok=True)
        with open(target_dir + os.sep + target_name + OwnerManager.CERT_SUFFIX, 'wb') as f:
            f.write(cert_pem)

        target_dir = base_dir + os.sep + 'msp' + os.sep + 'admincerts'
        os.makedirs(target_dir, exist_ok=True)
        if purpose in ('admin', 'member'):
            with open(target_dir + os.sep + target_name + OwnerManager.CERT_SUFFIX, 'wb') as f:
                f.write(cert_pem)

    @staticmethod
    def copy_msp_org_files(base_dir, root_pem_filename):

        rmtree(base_dir + os.sep + 'msp')

        target_dir = base_dir + os.sep + 'msp' + os.sep + 'cacerts'
        os.makedirs(target_dir, exist_ok=True)
        copyfile(root_pem_filename, target_dir + os.sep + os.path.basename(root_pem_filename))

        # FIX_ME: Add tls

        OwnerManager.copy_msp_admin_files(base_dir)