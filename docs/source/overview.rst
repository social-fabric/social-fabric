Overview
========

This page describes the blockchain component administration project

Purpose
-------

The goal of this project is to provide a web user interface, fast and easy to use, to help structure and deploy components of an hyperledger fabric network

By design, in order to simplify the user interface, several assumptions are taken:

 - It uses docker containers
 - The docker engine and this web server live on the same machine
 - The application is accessible with an HTML5 compatible browser (Chrome, Firefox, Edge, Safari, etc)
 - It creates Fabric Certificate Authorities (CA) to generate cryptographic material
 - Fabric CA servers are autonomous (self signed and not connected to LDAP)
 - There is one consortium for all orderers
 - Peers are grouped under the umbrella of an organization
 - Several organizations are allowed, each with several peers
 - Peers are deployed with CouchDB databases
 - Deployment is performed based on host names (dns names), no mapping to real ip addreses is provided
 - Configuration of firewalls, addresses and other related security config is outside of this scope
 - The server shall be placed under a web portal like nginx with tls encryption, since it conveys passwords

If you need a custom deployment out of previous assumptions, you may alter templates being used by the tool.
See Developpers guide for details on customization

Origin
------

The system is a generalisation, with assumptions, of the `test-network`_ of Hyperledger Fabric

Functionalities
---------------

Current functionalities include the initial deployment

 - Define components participating in the network
 - Deploy and activate the network
 - Create one or several channels
 - Deactivate the network
 - Reactivate the network

and defining and attaching a new organization to the network:

 - Define new components participating in the network
 - Deploy and activate the new components
 - Import the new org to the existing network
 - Join one or severals channela
 - Deactivate the new components
 - Reactivate the new components

.. _test-network: https://hyperledger-fabric.readthedocs.io/en/release-2.0/test_network.html