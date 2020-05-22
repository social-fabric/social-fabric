#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
from social_fabric.config_repo import ConfigRepo
from social_fabric.password_manager import PasswordManager


class User:

    def __init__(self, id, username, password):
        self._id = id
        self._username = username
        self._password = password
        self._authenticated = False

    def is_authenticated(self):
        return self._authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def has_username(self, username):
        return self._username == username

    def get_username(self):
        return self._username

    def authenticate(self, password):
        if self._password == PasswordManager.hash(password):
            self._authenticated = True
        return self._authenticated

    def set_password(self, password):
        self._password = PasswordManager.hash(password)

    def __str__(self):
        return self._username + ':' + self._password


class UserLoggon:

    user_dict = {}

    @classmethod
    def get_user_by_name(cls, username, password):
        for user_id in cls.user_dict:
            user = cls.user_dict[user_id]
            if user.has_username(username):
                if user.authenticate(password):
                    return user
        return None

    @classmethod
    def get_user_by_id(cls, id):
        if id in cls.user_dict:
            return cls.user_dict[id]
        return None

    @classmethod
    def add_user(cls, username, password):
        for userid in cls.user_dict:
            if cls.user_dict[userid]['username'] == username:
                return "User already exists"
        hashed_pass = PasswordManager.hash(password)
        id = str(len(cls.user_dict) + 1)
        cls.user_dict[id] = User(id, username, hashed_pass)
        return None

    @classmethod
    def modify_user(cls, username, password):
        for userid in cls.user_dict:
            if cls.user_dict[userid]['username'] == username:
                hashed_pass = PasswordManager.hash(password)
                cls.user_dict[id].set_password(hashed_pass)

    @classmethod
    def _save_user_dict_(cls):
        with open(ConfigRepo.ACCESS_FILE, 'w') as f:
            for userid in cls.user_dict:
                user = cls.user_dict[userid]
                f.write(str(user) + '\n')

    @classmethod
    def change_password(cls, username, old_pass, new_pass):
        user = cls.get_user_by_name(username, old_pass)
        if not user:
            return "User not found, password not changed"
        user.set_password(new_pass)
        cls._save_user_dict_()

    @classmethod
    def _load_users_(cls, data_path):
        with open(os.path.join(data_path, ConfigRepo.ACCESS_FILE), 'r') as f:
            lines = f.readlines()
            counter = 1
            for line in lines:
                content = line.split(':')
                if len(content) > 1:
                    username = content[0]
                    password = content[1].strip('\r').strip('\n')
                    cls.user_dict[str(counter)] = User(str(counter), username, password)
                    counter += 1

    @classmethod
    def init(cls, data_path):
        try:
            cls._load_users_(data_path)
        except:
            pass

