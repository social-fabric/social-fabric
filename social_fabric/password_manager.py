#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
from social_fabric.config_repo import ConfigRepo
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode


class PasswordManager:

    DISPLAYED_PASS = '********'

    @staticmethod
    def validate(clear_password):
        if not clear_password:
            return 'empty password'
        if len(clear_password) < 8:
            return 'password must contain at least 8 characters'
        if not any(ch.isdigit() for ch in clear_password):
            return 'password must contain at least one number'
        if not any(ch.isalpha() for ch in clear_password):
            return 'password must contain at least one letter'
        if not any(ch.isupper() for ch in clear_password):
            return 'password must contain at least one capitalized letter'
        if not any(ch in '[@_!#$%^&*()<>?/\|}{~:]' for ch in clear_password):
            return 'password must contain at least one special character'
        return None

    @classmethod
    def encrypt(cls, password):
        if not password:
            raise Exception('no password provided')
        fernet = Fernet(cls.key)
        return b64encode(fernet.encrypt(bytes(password, 'utf-8'))).decode('utf-8')

    @classmethod
    def decrypt(cls, password):
        if not password:
            raise Exception('no password provided')
        fernet = Fernet(cls.key)
        return fernet.decrypt(b64decode(bytes(password, 'utf-8'))).decode('utf-8')

    @classmethod
    def hash(cls, password):
        if not password:
            raise Exception('no password provided')
        kdf = Scrypt(salt=cls.salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
        return b64encode(kdf.derive(bytes(password, 'utf-8'))).decode('utf-8')

    @classmethod
    def init(cls, data_path):
        try:   # FIX_ME Might not be a good strategy!
            with open(os.path.join(data_path, ConfigRepo.ACCESS_SALT), 'rb') as f:
                cls.salt = f.read()
            with open(os.path.join(data_path, ConfigRepo.ACCESS_KEY), 'rb') as f:
                cls.key = b64decode(f.read())
        except:
            pass

    @classmethod
    def create_keys(cls, data_path, password):
        os.makedirs(os.path.join(data_path, ConfigRepo.ACCESS_DIR), exist_ok=True)
        cls.salt = os.urandom(16)
        with open(os.path.join(data_path, ConfigRepo.ACCESS_SALT), 'wb') as f:
             f.write(cls.salt)
        cls.key = Fernet.generate_key()
        with open(os.path.join(data_path, ConfigRepo.ACCESS_KEY), 'wb') as f:
            f.write(b64encode(cls.key))
        with open(os.path.join(data_path, ConfigRepo.ACCESS_FILE), 'w') as f:
            f.write('admin:' + cls.hash(password))




# Run once to create keys after installation
if __name__ == '__main__':
    PasswordManager.create_keys(os.getcwd(), 'admin')

