#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from datetime import datetime, timedelta
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class CertManager:

    @staticmethod
    def gen_signed_cert(root_key_filename, root_pem_filename, target_addr, purpose):

        with open(root_key_filename, "rb") as f:
            root_key = load_pem_private_key(f.read(), password=None, backend=default_backend())

        with open(root_pem_filename, "rb") as f:
            root_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

        target_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

        subject_country = None
        subject_state = None
        subject_locality = None
        for elem in root_cert.subject:
            if elem.oid._name == 'country':
                subject_country = elem.value
            elif elem.oid._name == 'state_or_province':
                subject_state = elem.value
            elif elem.oid._name == 'locality':
                subject_locality = elem.value

        subject_name_attributes = [x509.NameAttribute(NameOID.ORGANIZATION_NAME, target_addr)]
        if subject_country:
            subject_name_attributes.append(x509.NameAttribute(NameOID.COUNTRY_NAME, subject_country))
        if subject_state:
            subject_name_attributes.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject_state))
        if subject_locality:
            subject_name_attributes.append(x509.NameAttribute(NameOID.LOCALITY_NAME, subject_locality))
        subject_name_attributes.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, purpose))
        subject_name_attributes.append(x509.NameAttribute(NameOID.COMMON_NAME, target_addr))

        subject = x509.Name(subject_name_attributes)

        key_usage = x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=False,
                                  data_encipherment=False, key_agreement=False, key_cert_sign=False,
                                  crl_sign=False, encipher_only=None, decipher_only=None)
        basic_contraints = x509.BasicConstraints(ca=False, path_length=None)

        target_cert = (
            x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(root_cert.subject)
                .public_key(target_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=3650))
                .add_extension(key_usage, True)
                .add_extension(basic_contraints, True)
                .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), False)
                .sign(root_key, hashes.SHA256(), default_backend())
        )

        target_cert_pem = target_cert.public_bytes(encoding=serialization.Encoding.PEM)
        target_key_pem = target_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return target_cert_pem, target_key_pem

    # ----------------------------------------------------------------
    #                     Debugging Method
    # ----------------------------------------------------------------

    @staticmethod
    def read(filename):

        issuer_name = ''
        subject_name = ''
        subject_country = ''
        subject_state = ''
        subject_locality = ''

        with open(filename, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
            for elem in cert.issuer:
                #print(elem)
                if elem.oid._name == 'commonName':
                    issuer_name = elem.value
            for elem in cert.subject:
                #print(elem)
                if elem.oid._name == 'commonName':
                    subject_name = elem.value
                elif elem.oid._name == 'country':
                    subject_country = elem.value
                elif elem.oid._name == 'state_or_province':
                    subject_state = elem.value
                elif elem.oid._name == 'locality':
                    subject_locality = elem.value

            for ext in cert.extensions:
                print(ext)

            # -----------------------------------
            print('Certificate', filename)
            print('version:', cert.version)
            print('serial number:', cert.serial_number)
            print('public key:', cert.public_key())
            print('not valid before: ', cert.not_valid_before)
            print('not valid after: ', cert.not_valid_after)
            print('issuer')
            for elem in cert.issuer:
                 print('   ', elem.oid._name, elem.value)
            print('subject')
            for elem in cert.subject:
                 print('   ', elem.oid._name, elem.value)
            print('signature_hash_algorithm', cert.signature_hash_algorithm)
            # ---------------------------------

            return subject_name, issuer_name, subject_country, subject_state, subject_locality


if __name__ == '__main__':
    cert_manager = CertManager()

    filename = '<put a pem file here>'
    CertManager.read(filename)

