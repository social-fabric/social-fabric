/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let pageComponents =
    '<div class="p-vdiv-all">\n' +
    '   <div class="p-hdiv-top">\n' +
    '      <label class="p-obj-title" ><h1>Blockchain Component Administration</h1></label>\n' +
    '      <label class="p-help-link" onclick="window.open(\'docs/index.html\', \'_blank\')">help and documentation</label>\n' +
    '   </div>\n' +
    '   <div class="p-hdiv-middle">\n' +
    '      <h2><label id="pc-obj-consortium-addr" ></label></h2>\n' +
    '      <div id="pc-hdiv-add-button">\n' +
    '         <button id="pc-obj-button-add-orderer" onclick="pc_on_add_orderer()" >Add&nbsp;Orderer</button>\n' +
    '         <button id="pc-obj-button-add-org"  onclick="pc_on_add_organization()" >Add&nbsp;Organization</button>\n' +
    '          <button id="pc-obj-button-owner" onclick="pc_on_manage_owner()" >Edit&nbsp;Owners</button>\n' +
    '      </div>\n' +
    '   </div>\n' +
    '   <div id="pc-node-list-header" >\n' +
    '       <label id="pc-obj-label-addr" ><b>Address</b></label>\n' +
    '       <label id="pc-obj-label-type" ><b>Type</b></label>\n' +
    '       <label id="pc-obj-label-name" ><b>Name</b></label>\n' +
    '       <label id="pc-obj-label-ports" ><b>Ports</b></label>\n' +
    '       <div id="pc-obj-label-owner" ><b>Owner&nbsp;/&nbsp;Password</b></div>\n' +
    '       <label id="pc-obj-label-status" ><b>Status</b></label>\n' +
    '       <button id="pc-obj-hidden-button"  >Add&nbsp;Peer</button>\n' +
    '       <button id="pc-obj-hidden-button"  >Users</button>\n' +
    '       <button id="pc-obj-hidden-button"  >Remove</button>\n' +
    '   </div>\n' +
    '   <div id="pc-node-list" class="id="pc-node-list"></div>\n' +
    '   <div class="p-hdiv-bottom">\n' +
    '      <button id="pc-obj-button-deactivate" onclick="pc_on_deactivate()" >Deactivate</button>\n' +
    '      <button id="pc-obj-button-deploy" onclick="pc_on_deploy_activate()" >Deploy&nbsp;/&nbsp;Activate</button>\n' +
    '      <button id="pc-obj-button-manage-channel" onclick="pc_on_manage_channel()" disabled >Manage&nbsp;Channels</button>\n' +
    '   </div>\n' +
    '</div>';

pc_build_owner_list = function (owner) {
    let owner_list = '';
    let owner_selected = false;
    for (let ix = 0; ix < g_bcNodeData['owners'].length; ix++) {
        let elem = g_bcNodeData['owners'][ix]['addr'];
        owner_list += '<option value="' + elem + '"';
        if (elem === owner) {
            owner_list += ' selected ';
            owner_selected = true;
        }
        owner_list += '>' + elem + '</option>';
    }
    if (!owner_selected)
        owner_list = '<option disabled selected value> -- select a owner -- </option>' + owner_list;
    return owner_list;
};

pc_display_list = function(aList) {
    let htmlList = document.getElementById("pc-node-list");
    while (htmlList.firstChild)
        htmlList.removeChild(htmlList.firstChild);
    for (let ix = 0; ix < aList.length; ix++) {
        let add_peer_class = 'pc-obj-hidden-button';
        if (aList[ix]['type'] === 'organization')
            add_peer_class = 'pc-obj-button';
        let users_class = 'pc-obj-hidden-button';
        if (aList[ix]['type'] === 'organization' || (aList[ix]['type'] === 'consortium' && g_workingMode === 'CreateNetwork'))
            users_class = 'pc-obj-button';
        let remove_class = 'pc-obj-button';
        if (g_workingMode === 'AttachOrganizations' && (aList[ix]['type'] === 'orderer' || (aList[ix]['type'] === 'consortium')))
            remove_class = 'pc-obj-hidden-button';
        let owner_field = '';
        if (g_workingMode === 'CreateNetwork') {
            if (aList[ix]['type'] === 'organization' || aList[ix]['type'] === 'consortium') {
                owner_field = '   <div class="pc-div-owner" ><select id="pc-obj-owner-' + ix + '" class="pc-obj-select" onclick="pc_on_click_owner(' + ix + ')" onchange="pc_on_change_node_owner(' + ix + ')" >' + pc_build_owner_list(aList[ix]['owner']) + '</select></div>';
            }
            else {
                owner_field = '   <div class="pc-div-password" ><label id="pc-obj-password-' + ix + '" class="pc-obj-password" onclick="pc_on_change_node_password(' + ix + ')" >' + aList[ix]['password'] + '</label></div>';
            }
        }
        else {
            if (aList[ix]['type'] === 'consortium') {
                owner_field = '   <div class="pc-div-owner" ><label class="pc-obj-owner" >' + aList[ix]['owner'] + '</label></div>';
            }
            else if (aList[ix]['type'] === 'organization') {
                owner_field = '   <div class="pc-div-owner" ><select id="pc-obj-owner-' + ix + '" class="pc-obj-select" onclick="pc_on_click_owner(' + ix + ')" onchange="pc_on_change_node_owner(' + ix + ')" >' + pc_build_owner_list(aList[ix]['owner']) + '</select></div>';
            }
            else if (aList[ix]['type'] === 'orderer') {
                owner_field = '   <div class="pc-div-password" ><label class="pc-obj-password" >--------</label></div>';
            }
            else {
                owner_field = '   <div class="pc-div-password" ><label id="pc-obj-password-' + ix + '" class="pc-obj-password" onclick="pc_on_change_node_password(' + ix + ')" >' + aList[ix]['password'] + '</label></div>';
            }
        }
        let owner_text = 'Add&nbsp;Owner';
        if (aList[ix]['owner'])
            owner_text = aList[ix]['owner'];
        let div = document.createElement("div");
        div.className = "pc-node-list-row";
        div.innerHTML = '<label class="pc-obj-addr">' + aList[ix]['addr'] + '</label>'
                      + '<label class="pc-obj-type">' + aList[ix]['type'] + '</label>'
                      + '<input id="pc-obj-name-' + ix + '" class="pc-obj-name" value="' + aList[ix]['name'] + '" onchange="pc_on_change_node_name(' + ix + ')"/>'
                      + '<input id="pc-obj-ports-' + ix + '" class="pc-obj-ports" value="' + aList[ix]['ports'] + '" onchange="pc_on_change_node_ports(' + ix + ')"/>'
                      + owner_field
                      + '<label class="pc-obj-status">' + aList[ix]['status'] + '</label>'
                      + '<button class="' + add_peer_class + '" onclick="pc_on_add_peer(' + ix + ')" >Add&nbsp;Peer</button>'
                      + '<button class="' + users_class + '" onclick="pc_on_edit_users(' + ix + ')" >Users</button>'
                      + '<button class="' + remove_class + '" onclick="pc_on_remove_node(' + ix + ')" >Remove</button>';
        htmlList.appendChild(div);
    }
};

// --- Events ---

pc_on_deactivate = function () {
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    request.open('POST', 'deactivate');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
            }
            else {
                alert(this.responseText);
                pc_display_page1();
            }
        }
    };
    request.send(formData);
    display_console(pc_fetch_node_list);
};

pc_on_deploy_activate = function () {
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    request.open('POST', 'deployactivate');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
            }
            else {
                alert(this.responseText);
                pc_display_page1();
            }
        }
    };
    request.send(formData);
    display_console(pc_fetch_node_list);
};

pc_on_reactivate = function () {
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    request.open('POST', 'reactivate');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
            }
            else {
                alert(this.responseText);
                pc_display_page1();
            }
        }
    };
    request.send(formData);
    display_console(pc_fetch_node_list);
};

pc_on_manage_channel = function () {
    pch_display_page_channel()
};

pc_on_add_orderer = function () {
    let consortium = g_bcNodeData['addr'];
    let addr = window.prompt("Enter new orderer address:", consortium);
    if (!addr)
        return;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('addr', addr);
    request.open('POST', 'addorderer');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

pc_on_add_organization = function () {
    let consortium = g_bcNodeData['addr'];
    let addr = window.prompt("Enter new organization address:", consortium);
    if (!addr)
        return;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('addr', addr);
    request.open('POST', 'addorganization');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

pc_on_add_peer = function (ix) {
    let consortium = g_bcNodeData['name'];
    let org_addr = g_bcNodeData['nodes'][ix]['addr']
    let peer_addr = window.prompt("Enter new peer address:", org_addr);
    if (!peer_addr)
        return;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('orgaddr', org_addr);
    formData.append('peeraddr', peer_addr);
    request.open('POST', 'addpeer');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

pc_on_manage_owner = function () {
    p3_display_page3();
};

pc_on_remove_node = function (ix) {
    let consortium = g_bcNodeData['name'];
    let addr = g_bcNodeData['nodes'][ix]['addr'];
    if (window.confirm("Are you about to delete component " + addr + " Please, confirm")) {
        var request = new XMLHttpRequest();
        let formData = new FormData();
        formData.append('consortium', consortium);
        formData.append('nodeaddr', addr);
        request.open('POST', 'removenode');
        request.onreadystatechange = function () {
            if (this.readyState === 4) {
                if (this.status === 200) {
                    g_bcNodeData = JSON.parse(this.responseText);
                    pc_display_page1();
                } else {
                    alert(this.responseText);
                }
            }
        };
        request.send(formData);
    }
};

pc_on_change_node_name = function (ix) {
    let consortium = g_bcNodeData['name'];
    let addr = g_bcNodeData['nodes'][ix]['addr'];
    let name = document.getElementById('pc-obj-name-' + ix).value;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('nodename', name);
    formData.append('nodeaddr', addr);
    request.open('POST', 'setnodename');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

pc_on_change_node_ports = function (ix) {
    let consortium = g_bcNodeData['name'];
    let addr = g_bcNodeData['nodes'][ix]['addr'];
    let ports = document.getElementById('pc-obj-ports-' + ix).value;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('nodeaddr', addr);
    formData.append('ports', ports);
    request.open('POST', 'setnodeports');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

pc_on_change_node_password = function (ix) {

    prompt_password(function (password) {
        let consortium = g_bcNodeData['name'];
        let addr = g_bcNodeData['nodes'][ix]['addr'];

        var request = new XMLHttpRequest();
        let formData = new FormData();
        formData.append('consortium', consortium);
        formData.append('nodeaddr', addr);
        formData.append('password', password);
        request.open('POST', 'setnodepassword');
        request.onreadystatechange = function() {
            if (this.readyState === 4) {
                if (this.status === 200) {
                    g_bcNodeData = JSON.parse(this.responseText);
                    pc_display_page1();
                }
                else {
                    alert(this.responseText);
                }
            }
        };
        request.send(formData);
    });
};

pc_on_click_owner = function (ix) {
    let consortium = g_bcNodeData['name'];
    let addr = g_bcNodeData['nodes'][ix]['addr'];

};

pc_on_change_node_owner = function (ix) {
    let consortium = g_bcNodeData['name'];
    let addr = g_bcNodeData['nodes'][ix]['addr'];
    let owner = document.getElementById('pc-obj-owner-' + ix).value;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('nodeaddr', addr);
    formData.append('nodeowner', owner);
    request.open('POST', 'setnodeowner');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

pc_on_edit_users = function (ix) {
    let addr = g_bcNodeData['nodes'][ix]['addr'];
    puser_display_page5(addr);
};

// --- Loader ---
pc_has_all_active_server = function(aList) {
    for (let ix = 0; ix < aList.length; ix++) {
        if (aList[ix]['status'] === '------')
            continue;
        if (aList[ix]['status'] !== 'active')
            return false;
    }
    return true;
};

pc_display_page1 = function () {
                if (g_popup_active)
                    return;
                let focusElementId = document.activeElement.id;
                document.getElementById("body").innerHTML = pageComponents;
                document.getElementById('pc-obj-consortium-addr').textContent = g_bcNodeData['addr'];
                if (g_workingMode === 'CreateNetwork') {
                    document.getElementById('pc-obj-button-add-orderer').style.display = 'block';
                }
                else if (g_workingMode === 'AttachOrganizations') {
                    document.getElementById('pc-obj-button-add-orderer').style.display = 'none';
                }
                // --- refresh the list
                pc_display_list(g_bcNodeData['nodes']);

                if (pc_has_all_active_server(g_bcNodeData['nodes'])) {
                    document.getElementById('pc-obj-button-manage-channel').disabled = false;
                }
                if (g_bcNodeData['deployed']) {
                    document.getElementById('pc-obj-button-deploy').innerText = 'Reactivate';
                    document.getElementById('pc-obj-button-deploy').onclick = pc_on_reactivate;
                }
                let focusElement = document.getElementById(focusElementId);
                if (focusElement)
                    focusElement.focus();
};

pc_fetch_node_list = function () {
    var request = new XMLHttpRequest();
    request.open('GET', 'getnodelist');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pc_display_page1();
            }
            else {
                alert("No connection with the blockchain network");
                window.close();
            }
        }
    };
    request.send();
};
