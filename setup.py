from setuptools import setup, find_packages

setup(
    name='social_fabric',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    url='https://social-fabric.io',
    license='(C) Neptunium Inc.',
    author='Francois Robert',
    author_email='francois.robert@hotmail.com',
    description='A user friendly way to deploy Hyperledger Fabric (tm) components',
    python_requires='>=3.7',
    setup_requires=['wheel'],
    install_requires=['click', 'Flask', 'Flask-Login', 'itsdangerous', 'Jinja2',
                      'MarkupSafe', 'cryptography', 'requests', 'Werkzeug']
)
