#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from social_fabric.config_repo import ConfigRepo

class NetworkTemplateProcessor:

    def __init__(self):
        self.file_loader = FileSystemLoader(ConfigRepo.TEMPLATE_SRC_DIR)
        self.env = Environment(loader=self.file_loader, undefined=StrictUndefined)

    def process(self, filename, *args, **kwargs):
        template = self.env.get_template(filename)
        return template.render(*args, **kwargs)


if __name__ == '__main__':
    config = {}
    net_template_processor = NetworkTemplateProcessor()

    output = net_template_processor.process('docker-compose-ca.yaml',
                                            BCC_NETWORK_DOMAIN='orsnet',
                                            BCC_CA_ADDR='ca.theobjects.com',
                                            BCC_CA_PORT='7055',
                                            BCC_CA_PUBLIC_CERT='ca.theobjects.com.cert.pem',
                                            BCC_CA_PRIVATE_KEY='ca.theobjects.com.priv.key',
                                            BCC_CA_ADMIN_NAME='admin', BCC_CA_ADMIN_PASSWORD='adminpw')
    with open('/tmp/docker-compose.yaml', 'w') as f:
        f.write(output)
