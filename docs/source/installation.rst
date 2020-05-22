Installation
============

The SocialFabric is a Web server that can be deployed on Linux server and that is access with an HTML5
compatible browser (Chrome, Firefox, Edge, etc.)

Prerequisites
-------------

In order to deploy this application, you will need

 - A Linux server
 - docker
 - docker-compose

The application should run on any standard Linux distribution having the x86_64 hardware architecture.

To install docker, follow your Linux distribution instructions

  RedHat and CentOS Servers

   ``sudo yum install docker``

  Suse Server

    ``sudo zypper install docker``

  Ubuntu Server

    ``apt-get install docker``

To install docker-compose, follow your Linux distribution instructions

  RedHat and CentOS Servers

    ``sudo yum install docker``

  Suse Server

    ``sudo zypper install docker``

  Ubuntu Server

    ``apt-get install docker``

We strongly suggest that you refer to your Linux distribution documentation for further details.

Recommended Practice
--------------------

When installing a service, most Linux distribution recommend that you first create a specific user, with
limited priviledges, for it.

**Do not install the service with root privileges**

To create a new user called *socialfabric*, type

    ``sudo adduser socialfabric -d /home/socialfabric``

If you whish to access this account directly, you may add a password

    ``sudo passwd socialfabric``

To create and manage user account, please refer to your Linux distribution

Binary Distribution
-------------------

The server is available as a binary distribution that includes Hyperledger Fabric Components, compatible
with the *x86_64* architecture Linux server.

Download the binary on your chosen directory, for instance ``/home/socialfabric``

Installation and Configuration
------------------------------

To install and configure the web server, lunch the application with no argument

    ``./SocialFabric``

The following lines will appear

    ``usage: python app.py --config <config file>``

    ``Do you want to install and configure the application? [Y/n]:``

Type *enter* to install and configure the application.

If docker and docker-compose are properly installed, you should see something like

    ``Verifying prerequisites``

    ``Docker version 18.09.7, build 2d0083d found``

    ``docker-compose version 1.25.0, build 0a186604 found``

The installation process stops if requirements are not met.

The process will ask for server name and port number

    ``server hostname [localhost]:``

    ``listening port [5000]:``

Unless required, keep those values by typing *enter* twice.

Note: This is not the public address of the server, nor the public port number. A Web portal, like nginx or apache, shall redirect to this service.
 
Data diretory is where the installation process will create the directory tree structure containg data and json files.

    ``Data directory [/home/orsblockchain]:``

Type *enter* to keep this dorectory or give another one.

The web server relies on a configuration file given at startup. By default, the installation
process propose a sub diretory under the data directory called *config*. You may change it to something
like ``/etc/orsblockchain`` if desired.

   ``Path for the configuration file [/home/orsblockchain/config]:``

If a directory does not exist, the system may ask if you want to create it.

   ``Config path "/home/frobert/essai/config" does not exist. Do you want to create it? [Y/n]:``

Finally, give an administrator password

    ``Administrator's password:``

and confirm it

    ``Confirm (re-enter) password:``

Password should have at lest one letter, one number, one special character and a at least 8 characters

At this point, the installation process will pull all required Hyperledger Fabric Docker Images,
create encryption keys, store password and create the configuration file.

You should see something like:

    ``configuration file /home/orsblockchain/config/OrsBlockchain.json created``

    ``Installation and configuration completed``

    ``You may start the server with:``

        ``/home/orsblockchain/OrsBlockchain --config /home/orsblockchain/config/OrsBlockchain.json``

Start the Web Server
--------------------

To start the server, you need a configuration file.

    OrsBlockchain --config <Configuration file>

see previous section to install the server and create a configuration file.

Test the Web Server Locally
---------------------------

If you have access to a browser on the Linux server, you may lunch it with the following command

   `http://localhost:8080 <https://localhost:8080>`__

You will be prompted with a username and a password

    username is *admin* and password is the one given during installation.

See the user guide section for more details on how to use the application.

Next steps
----------

Your server is now running locally on your Linux server, but since most Linux distribution includes a Firewall that
prevents mapping ports above 1024 to the external world, you have to put a portal in front of it, with
TLS (https) encryption, since password are conveyed between the browser and the server.

Also,

Once your blockchain components are configured and deployed, you will also need to map to the external world
ports and adresses of your docker components.
