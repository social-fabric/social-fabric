#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

import os
import sys
import json
import random
import logging
from logging.handlers import RotatingFileHandler
from getopt import getopt, GetoptError
from flask import Flask, session, Response, request, redirect, render_template, send_from_directory, abort
from flask_login import LoginManager, login_required, login_user, current_user
from flask.logging import default_handler
from social_fabric.installation import Install
from social_fabric.password_manager import PasswordManager
from social_fabric.user_logon import UserLoggon
from social_fabric.config_repo import ConfigRepo
from social_fabric.owner_manager import OwnerManager
from social_fabric.user_manager import UserManager
from social_fabric.component_manager import ComponentManager
from social_fabric.channel_manager import ChannelManager
from social_fabric.deploy_manager import DeployManager


# --------------------------------
# Instantiation of the application
# --------------------------------
app = Flask(__name__)

# --------------------------------
#        Configuration
# --------------------------------
config_file = None
try:
    opts, args = getopt(sys.argv[1:], "c:", ["config="])
except GetoptError:
    print('usage: python app.py --config <config file>')
    Install.main()
    sys.exit(-1)
for opt, arg in opts:
    if opt in ('-c, --config'):
        config_file = arg
if not config_file:
    print('usage: python app.py --config <config file>')
    Install.main()
    sys.exit(-1)
app.config.from_json(config_file)

# Change base directory to the data directory found in configuration.
# All paths will be relative to that
ConfigRepo.set_directories(app.config)
os.chdir(ConfigRepo.DATA_REPO)

# --------------------------------
#       Logger Settings
# --------------------------------
root = logging.getLogger()
root.addHandler(default_handler)
log = logging.getLogger('werkzeug')
rotating_handler = RotatingFileHandler(app.config['LOG_PATH'] + os.sep + 'SocialFabric.log',
                                    maxBytes=app.config['LOG_MAX_SIZE'],
                                    backupCount=app.config['LOG_MAX_FILES'])
root.addHandler(rotating_handler)
log.addHandler(rotating_handler)
app.logger.addHandler(rotating_handler)

if app.config['DEBUG']:
    log.setLevel(logging.DEBUG)
    root.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)
    root.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)

app.logger.info('SocialFabric Component Administration Started')
app.logger.info('SocialFabric Configuration File: ' + config_file)
app.logger.info('SocialFabric Bin Directory: ' + ConfigRepo.BIN_REPO)
app.logger.info('SocialFabric Data Directory: ' + ConfigRepo.DATA_REPO)
app.logger.info('SocialFabric Log Directory: ' + app.config['LOG_PATH'])

# ----------------------------
#        flask-login
# ----------------------------

PasswordManager.init(app.config['DATA_PATH'])
UserLoggon.init(app.config['DATA_PATH'])
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "do_login"

# ----------------------------
#       managers
# ----------------------------
app.user_manager = UserManager()
app.owner_manager = OwnerManager()
app.component_manager = ComponentManager(app.config, app.owner_manager)


# FIX_ME
# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return UserLoggon.get_user_by_id(user_id)


# ------------------------
#        Routes
# ------------------------

@app.route('/')
def do_root():
    return redirect('/main')

# -------- Login ---------


@app.route('/login', methods=['GET'])
def do_login():
    last_login_msg = ''
    if 'last_login_msg' in session:
        last_login_msg = session['last_login_msg']
    return render_template('login.html', MESSAGE=last_login_msg)

@app.route('/logon', methods=['POST'])
def do_logon():
    username = request.form['username']
    password = request.form['password']
    user = UserLoggon.get_user_by_name(username, password)
    if user:
        login_user(user)
        session['last_login_msg'] = ''
        return redirect('/main')
    else:
        session['last_login_msg'] = 'Invalid Username or Password'
        return redirect('/login?dummy=' + str(random.randint(1,100))) # abort(401)

@app.route('/changeadminpassword', methods=['POST'])
@login_required
def do_change_admin_password():
    username = current_user.get_username()
    old_pass = request.form['oldpass']
    new_pass = request.form['newpass']
    msg = UserLoggon.change_password(username, old_pass, new_pass)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response("password changed", status=200, mimetype='text/plain')


# ---- Documentation ---
@app.route('/docs/<path:text>')
def do_docs(text):
    return send_from_directory('docs', text)

@app.route('/main', methods=['GET'])
@login_required
def do_main():
    return render_template('main.html')

@app.route('/getworkingmode', methods=['GET'])
@login_required
def do_get_working_mode():
    working_mode, working_dir = ConfigRepo.load_working_conf()
    if working_dir:
        ConfigRepo.set_network(working_dir)
    return Response(working_mode, status=200, mimetype='text/plain')

# -------- Mode Management ---------


@app.route('/setworkingmode', methods=['POST'])
@login_required
def do_set_working_mode():

    working_mode = request.form['workingmode']
    returned_mode = ConfigRepo.set_working_mode(working_mode)

    if working_mode == 'Create':
        consortium_name = request.form['consortiumname']
        consortium_addr = request.form['consortiumaddr']
        msg, node_list = app.component_manager.add_consortium(consortium_name, consortium_addr)
        if msg:
            return Response(msg, status=500, mimetype='text/plain')
    elif working_mode == 'Attach':
        consortium_name = request.form['consortiumname']
        consortium_addr = request.form['consortiumaddr']
        orderer_name = request.form['orderername']
        orderer_addr = request.form['ordereraddr']
        orderer_port = request.form['ordererport']
        orderer_cert = request.form['orderercert']
        msg, node_list = app.component_manager.attach_orderer(consortium_name, consortium_addr, orderer_name,
                                                              orderer_addr, orderer_port, orderer_cert)
        if msg:
            return Response(msg, status=500, mimetype='text/plain')
    return Response(returned_mode, status=200, mimetype='text/plain')

# -------- Node Management ---------


@app.route('/addconsortium', methods=['POST'])
@login_required
def do_add_consortium():
    name = request.form['name']
    addr = request.form['addr']
    msg, node_list = app.component_manager.add_consortium(name, addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/getnodelist', methods=['GET'])
@login_required
def do_get_node_list():
    msg, node_list = app.component_manager.get_node_list()
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')

@app.route('/addorderer', methods=['POST'])
@login_required
def do_add_orderer():
    consortium = request.form['consortium']
    addr = request.form['addr']
    msg, node_list = app.component_manager.add_orderer(consortium, addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/addorganization', methods=['POST'])
@login_required
def do_add_organizer():
    consortium = request.form['consortium']
    addr = request.form['addr']
    msg, node_list = app.component_manager.add_organization(consortium, addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/addpeer', methods=['POST'])
@login_required
def do_add_peer():
    consortium = request.form['consortium']
    orgaddr = request.form['orgaddr']
    peeraddr = request.form['peeraddr']
    msg, node_list = app.component_manager.add_peer(consortium, orgaddr, peeraddr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/removenode', methods=['POST'])
@login_required
def do_remove_node():
    consortium = request.form['consortium']
    node_addr = request.form['nodeaddr']
    msg, node_list = app.component_manager.remove_node(node_addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/setnodename', methods=['POST'])
@login_required
def do_set_node_addr():
    consortium = request.form['consortium']
    node_name = request.form['nodename']
    node_addr = request.form['nodeaddr']
    msg, node_list = app.component_manager.set_name(node_addr, node_name)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/setnodeports', methods=['POST'])
@login_required
def do_set_node_ports():
    consortium = request.form['consortium']
    node_addr = request.form['nodeaddr']
    node_ports = request.form['ports']
    msg, node_list = app.component_manager.set_ports(node_addr, node_ports)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/setnodepassword', methods=['POST'])
@login_required
def do_set_node_password():
    consortium = request.form['consortium']
    node_addr = request.form['nodeaddr']
    password = request.form['password']
    msg, node_list = app.component_manager.set_password(node_addr, password)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/setnodeowner', methods=['POST'])
@login_required
def do_set_node_owner():
    consortium = request.form['consortium']
    node_addr = request.form['nodeaddr']
    node_owner = request.form['nodeowner']
    msg, node_list = app.component_manager.set_owner(node_addr, node_owner)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


# -------- Owner Management --------


@app.route('/getownerlist', methods=['GET'])
@login_required
def do_get_owner_list():
    msg, owner_list = app.owner_manager.get_owner_list()
    if msg:
       return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(owner_list), status=200, mimetype='application/json')


@app.route('/deleteowner', methods=['POST'])
@login_required
def do_delete_owner():
    addr = request.form['addr']
    msg, owner_list = app.owner_manager.delete_owner(addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(owner_list), status=200, mimetype='application/json')


@app.route('/addowner', methods=['POST'])
@login_required
def do_add_owner():
    org = request.form['org']
    country = request.form['country']
    state = request.form['state']
    locality = request.form['locality']
    addr = request.form['addr']
    catype = request.form['catype']
    caroot = request.form['caroot']
    msg, owner_list = app.owner_manager.add_owner(org, country, state, locality, addr, catype, caroot)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(owner_list), status=200, mimetype='application/json')


@app.route('/setownerpassword', methods=['POST'])
@login_required
def do_set_owner_password():
    addr = request.form['addr']
    password = request.form['password']
    msg, owner_list = app.owner_manager.set_password(addr, password)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(owner_list), status=200, mimetype='application/json')


@app.route('/genownercert', methods=['POST'])
@login_required
def do_gen_owner_cert():
    org = request.form['org']
    country = request.form['country']
    state = request.form['state']
    locality = request.form['locality']
    addr = request.form['addr']
    msg, new_owner_dict = OwnerManager.gen_owner_cert(org, country, state, locality, addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(new_owner_dict), status=200, mimetype='application/json')


@app.route('/importownercert', methods=['POST'])
@login_required
def do_import_owner_cert():
    org = request.form['org']
    country = request.form['country']
    state = request.form['state']
    locality = request.form['locality']
    addr = request.form['addr']
    if 'file' not in request.files:
        return Response('{"message":"No file argument"}', status=500, mimetype='application/json')
    file = request.files['file']
    msg, new_owner_dict = OwnerManager.import_owner_cert(org, country, state, locality, addr, file)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(new_owner_dict), status=200, mimetype='application/json')


# -------- User Management ---------


@app.route('/getuserlist', methods=['GET'])
@login_required
def do_get_user_list():
    addr = request.args.get('addr')
    msg, user_list = app.user_manager.get_user_list(addr)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/adduser', methods=['POST'])
@login_required
def do_add_user():
    addr = request.form['addr']
    username = request.form['username']
    msg, user_list = app.user_manager.add_user(addr, username)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='text/plain')


@app.route('/deleteuser', methods=['POST'])
@login_required
def do_delete_user():
    addr = request.form['addr']
    username = request.form['username']
    msg, user_list = app.user_manager.delete_user(addr, username)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setrealusername', methods=['POST'])
@login_required
def do_set_real_user_name():
    addr = request.form['addr']
    username = request.form['username']
    realname = request.form['realname']
    msg, user_list = app.user_manager.set_name(addr, username, realname)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setuserpassword', methods=['POST'])
@login_required
def do_set_user_password():
    addr = request.form['addr']
    username = request.form['username']
    password = request.form['password']
    msg, user_list = app.user_manager.set_password(addr, username, password)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setuseradmin', methods=['POST'])
@login_required
def do_set_user_admin():
    addr = request.form['addr']
    username = request.form['username']
    admin = request.form['admin'] == 'true'
    msg, user_list = app.user_manager.set_admin(addr, username, admin)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setusercreate', methods=['POST'])
@login_required
def do_set_user_create():
    addr = request.form['addr']
    username = request.form['username']
    create = request.form['create'] == 'true'
    msg, user_list = app.user_manager.set_create(addr, username, create)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setusercopy', methods=['POST'])
@login_required
def do_set_user_copy():
    addr = request.form['addr']
    username = request.form['username']
    copy = request.form['copy'] == 'true'
    msg, user_list = app.user_manager.set_copy(addr, username, copy)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setuserconceal', methods=['POST'])
@login_required
def do_set_user_conceal():
    addr = request.form['addr']
    username = request.form['username']
    conceal = request.form['conceal'] == 'true'
    msg, user_list = app.user_manager.set_conceal(addr, username, conceal)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


@app.route('/setuserdelete', methods=['POST'])
@login_required
def do_set_user_delete():
    addr = request.form['addr']
    username = request.form['username']
    delete = request.form['delete'] == 'true'
    msg, user_list = app.user_manager.set_delete(addr, username, delete)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(user_list), status=200, mimetype='application/json')


# -------- Channel Management ---------


@app.route('/getchannellist', methods=['GET'])
@login_required
def do_get_channel_list():
    session['channellist'] = ChannelManager.get_list(app.component_manager)
    return Response(json.dumps(session['channellist']), status=200, mimetype='application/json')



@app.route('/createchannel', methods=['POST'])
@login_required
def do_create_channel():
    consortium = request.form['consortium']
    channel_name = request.form['channelname']
    msg, node_list, session['executelist'] = ChannelManager.create_channel(app.component_manager, channel_name)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/exportorderer', methods=['POST'])
@login_required
def do_export_orderer():
    consortium = request.form['consortium']
    msg, content = ChannelManager.export_orderer(app.component_manager)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(content), status=200, mimetype='text/plain')


@app.route('/exportorganization', methods=['POST'])
@login_required
def do_export_organization():
    consortium = request.form['consortium']
    msg, content = ChannelManager.export_organization(app.component_manager)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(content, status=200, mimetype='text/plain')


@app.route('/joinchannel', methods=['POST'])
@login_required
def do_attach_channel():
    consortium = request.form['consortium']
    channel_name = request.form['channelname']
    msg, node_list, session['executelist'] = ChannelManager.join_channel(app.component_manager, channel_name)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/addorgtochannel', methods=['POST'])
@login_required
def do_add_org_to_channel():
    consortium = request.form['consortium']
    channel = request.form['channel']
    file_content = request.form['filecontent']
    msg, node_list, session['executelist'] = ChannelManager.add_org_to_channel(app.component_manager, channel, file_content)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


# -------- Deploy Management ---------


@app.route('/deployactivate', methods=['POST'])
@login_required
def do_deploy_activate():
    consortium = request.form['consortium']
    msg, node_list, session['executelist'] = DeployManager.deploy_activate(app.component_manager)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/reactivate', methods=['POST'])
@login_required
def do_reactivate():
    consortium = request.form['consortium']
    msg, node_list, session['executelist'] = DeployManager.reactivate(app.component_manager)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/deploy', methods=['POST'])
@login_required
def do_deploy():
    consortium = request.form['consortium']
    execute_list = session['executelist']
    _, component_dict = app.component_manager.get_node_list()
    msg, node_list, session['executelist'] = DeployManager.deploy(component_dict, execute_list)
    if msg:
        if msg == 'done':
            return Response('done', status=201, mimetype='text/plain')
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/createjoinchannel', methods=['POST'])
@login_required
def do_create_join_channel():
    consortium = request.form['consortium']
    _, component_dict = app.component_manager.get_node_list()
    msg, node_list = DeployManager.create_join_channel(component_dict)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')


@app.route('/deactivate', methods=['POST'])
@login_required
def do_deactivate():
    consortium = request.form['consortium']
    _, component_dict = app.component_manager.get_node_list()
    msg, node_list, session['executelist'] = DeployManager.deactivate(component_dict)
    app.component_manager.refresh_status(component_dict)
    if msg:
        return Response(msg, status=500, mimetype='text/plain')
    return Response(json.dumps(node_list), status=200, mimetype='application/json')




# ------------------------------------------------------
# For development, start the application from that point
#
#   python app.py --config config/SocialFabric.json
#
# ------------------------------------------------------
if __name__ == '__main__':
    os.system('google-chrome -incognito http://localhost:5000 &')
    app.run()

