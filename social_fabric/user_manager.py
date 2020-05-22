#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import json
from shutil import rmtree
from social_fabric.config_repo import ConfigRepo
from social_fabric.owner_manager import OwnerManager
from social_fabric.password_manager import PasswordManager

class UserManager:

    def __init__(self):
        self.user_list = {}

    @staticmethod
    def _find_user_path_(addr, user):
        users_path = UserManager._find_all_users_path_(addr)
        for elem in os.listdir(users_path):
            if elem == user:
                return users_path + os.sep + user

    @staticmethod
    def _save_user_dict_(user_dict, user_path, user):
        filename = user_path + os.sep + user + '.json'
        with open(filename, 'w') as f:
            json.dump(user_dict, f)

    @staticmethod
    def _load_user_dict_(user_path, user):
        filename = user_path + os.sep + user + '.json'
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                user_dict = json.load(f)
        else:
            user_dict = {"addr": user, "name": "", "password": "", "admin": False, "create": False, "copy": False,
                         "conceal": False, "delete": False}
            with open(filename, 'w') as f:
                json.dump(user_dict, f)
        return user_dict

    @staticmethod
    def _build_user_list_(addr, with_password=False):
        user_list = []
        all_users_path = UserManager._find_all_users_path_(addr)
        if not all_users_path:
            return 'addr ' + addr + ' not found', None
        users = os.listdir(all_users_path)
        for user in users:
            user_dict = UserManager._load_user_dict_(all_users_path + os.sep + user, user)
            if not with_password:
                if user_dict['password']:
                    user_dict['password'] = PasswordManager.DISPLAYED_PASS
                else:
                    user_dict['password'] = ''
            user_list.append(user_dict)
        return None, user_list

    @staticmethod
    def _find_all_users_path_(addr):

        # Search in consortium
        consortium_list = os.listdir(ConfigRepo.ORDERER_SRC_REPO)
        for elem in consortium_list:
            if elem == addr:
                return ConfigRepo.ORDERER_SRC_REPO + os.sep + addr + os.sep + 'users'

        # Search in organization
        organization_list = os.listdir(ConfigRepo.PEER_SRC_REPO)
        for elem in organization_list:
            if elem == addr:
                return ConfigRepo.PEER_SRC_REPO + os.sep + addr + os.sep + 'users'
        # Not found
        return None

    # ----------------------------------------------------
    #                   Public Methods
    # ----------------------------------------------------

    @staticmethod
    def find_all_users(addr):
        users_path = UserManager._find_all_users_path_(addr)
        if users_path:
            return os.listdir(users_path)
        return []

    @staticmethod
    def get_user_dict(org_addr, user):
        user_path = UserManager._find_user_path_(org_addr, user)
        return UserManager._load_user_dict_(user_path, user)

    @staticmethod
    def find_first_admin_user(addr):
        user_list = UserManager.find_all_users(addr)
        for user in user_list:
            user_dict = UserManager.get_user_dict(addr, user)
            if user_dict['admin']:
                return user
        return None

    # ---- Instance Methods ----

    def validate(self, addr):
        return True

    def add_user(self, addr, new_username):
        # Verify that the name is valid
        if ' ' in new_username:
            return 'space are not permitted in username', None
        # FIX_ME: filter special character
        if '@' in new_username:
            names = new_username.split('@')
            if names[1] != addr:
                return 'username ' + new_username + ' does not match ' + addr + ' domain', None
            username = new_username
        else:
            username = new_username + '@' + addr

        all_users_path = UserManager._find_all_users_path_(addr)
        if not all_users_path:
            return 'addr ' + addr + ' not found', None
        user_path = all_users_path + os.sep + username
        if os.path.exists(user_path):
            return 'username ' + username + ' already exists', None
        os.mkdir(user_path)
        os.mkdir(user_path + os.sep + 'msp')
        os.mkdir(user_path + os.sep + 'tls')
        user_dict = {"addr": username, "name": "", "password": "", "admin": False, "create": False, "copy": False, "conceal": False, "delete": False}
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def delete_user(self, addr, username):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        rmtree(user_path)
        return self._build_user_list_(addr)

    def set_name(self, addr, username, name):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['name'] = name
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def set_password(self, addr, username, password):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['password'] = PasswordManager.encrypt(password)
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def set_admin(self, addr, username, admin):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['admin'] = admin
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def set_create(self, addr, username, create):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['create'] = create
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def set_copy(self, addr, username, copy):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['copy'] = copy
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def set_conceal(self, addr, username, conceal):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['conceal'] = conceal
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def set_delete(self, addr, username, delete):
        user_path = UserManager._find_user_path_(addr, username)
        if not user_path:
            return 'username ' + username + 'of addr ' + addr + ' not found', None
        user_dict = UserManager._load_user_dict_(user_path, username)
        user_dict['delete'] = delete
        UserManager._save_user_dict_(user_dict, user_path, username)
        return self._build_user_list_(addr)

    def get_user_list(self, addr, with_password=False):
        return self._build_user_list_(addr, with_password)

    # -------------------------------------------------------------
    #                  Generate Certificates
    # -------------------------------------------------------------

    @staticmethod
    def gen_certificates(addr, root_name, root_pem_filename):
        users_path = UserManager._find_all_users_path_(addr)
        for username in os.listdir(users_path):
            target_dir = users_path + os.sep + username
            # FIX_ME: Add proper purpose
            OwnerManager.gen_msp_cert_files(root_name, root_pem_filename, target_dir, username, 'admin')

