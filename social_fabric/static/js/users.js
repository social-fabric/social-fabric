/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let pageUsers = ''
    + '<div id="vdiv0">\n'
    + '</div>\n'
    + '<div class="p-vdiv-all">\n'
    + '   <div class="p-hdiv-top">\n'
    + '      <h1><label id="puser-obj-title" class="p-obj-title" >Blockchain User Administration</label></h1>\n'
    + '      <label class="p-help-link" onclick="window.open(\'docs/html/index.html\', \'_blank\')">help and documentation</label>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-middle">\n'
    + '      <h2><label id="puser-obj-target" ></label></h2>\n'
    + '      <button id="puser-obj-add-user"  onclick="puser_on_add_user()" >Add User</button>\n'
    + '   </div>\n'
    + '   <div id="puser-vdiv-middle">\n'
    + '      <div id="puser-user-list-header" >'
    + '          <label id="puser-obj-label-username" >User name</label>\n'
    + '          <label id="puser-obj-label-realname" >Name</label>\n'
    + '          <label id="puser-obj-label-password" >Password</label>\n'
    + '          <label id="puser-obj-label-admin" >Admin</label>\n'
    + '          <label id="puser-obj-label-create" >Create</label>\n'
    + '          <label id="puser-obj-label-copy" >Copy</label>\n'
    + '          <label id="puser-obj-label-conceal" >Conceal</label>\n'
    + '          <label id="puser-obj-label-delete" >Delete</label>\n'
    + '          <button id="puser-obj-hidden-button-delete" >Delete</button>\n'
    + '      </div>\n'
    + '      <div id="puser-user-list">\n'
    + '      </div>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-bottom">\n'
    + '      <button id="puser-obj-button-close"  onclick="puser_on_close_page5()" >Close</button>\n'
    + '   </div>\n'
    + '</div>\n';

var puser_orgAddr = '';
var puser_userList = [];

puser_isChecked = function(checked) {
   if (checked)
      return 'checked';
   return '';
};

puser_display_user_list = function(aList) {
    if (g_popup_active)
        return;
    let focusElementId = document.activeElement.id;
    let htmlList = document.getElementById("puser-user-list");
    while (htmlList.firstChild)
        htmlList.removeChild(htmlList.firstChild);
    for (ix = 0; ix < aList.length; ix++) {
        let div = document.createElement("div");
        div.className = "puser-user-list-row";
        div.innerHTML = '<label id="puser-obj-username-' + ix + '" class="puser-obj-username">' + aList[ix]['addr'] + '</label>'
                      + '<input id="puser-obj-realname-' + ix + '" class="puser-obj-realname" value="' + aList[ix]['name'] + '" onchange="puser_on_change_user_name(' + ix + ')" />'
                      + '<label type="password" id="puser-obj-password-' + ix + '" class="puser-obj-password" onclick="puser_on_change_user_password(' + ix + ')" >' + aList[ix]['password'] + '</label>'
                      + '<div class="puser-obj-div-admin">'
                      + '   <input type="checkbox"  id="puser-obj-admin-' + ix + '" class="puser-obj-admin" onchange="puser_on_change_user_admin(' + ix + ')" ' + puser_isChecked(aList[ix]['admin']) + ' />'
                      + '</div>'
                      + '<div class="puser-obj-div-create">'
                      + '   <input type="checkbox"  id="puser-obj-create-' + ix + '" class="puser-obj-create" onchange="puser_on_change_user_create(' + ix + ')" ' + puser_isChecked(aList[ix]['create']) + ' />'
                      + '</div>'
                      + '<div class="puser-obj-div-copy">'
                      + '   <input type="checkbox"  id="puser-obj-copy-' + ix + '" class="puser-obj-copy" onchange="puser_on_change_user_copy(' + ix + ')" ' + puser_isChecked(aList[ix]['copy']) + ' />'
                      + '</div>'
                      + '<div class="puser-obj-div-conceal">'
                      + '   <input type="checkbox"  id="puser-obj-conceal-' + ix + '" class="puser-obj-conceal" onchange="puser_on_change_user_conceal(' + ix + ')" ' + puser_isChecked(aList[ix]['conceal']) + ' />'
                      + '</div>'
                      + '<div class="puser-obj-div-delete">'
                      + '   <input type="checkbox"  id="puser-obj-delete-' + ix + '" class="puser-obj-delete" onchange="puser_on_change_user_delete(' + ix + ')" ' + puser_isChecked(aList[ix]['delete']) + ' />'
                      + '</div>'
                      + '<button class="puser-obj-button-delete" onclick="puser_on_delete_user(' + ix + ')" >Delete</button>';
        htmlList.appendChild(div);
    }
    let focusElement = document.getElementById(focusElementId);
    if (focusElement)
        focusElement.focus();
};

// --- Events ---

puser_on_close_page5 = function () {
   pc_display_page1();
};

puser_on_add_user = function () {
    let newUser = window.prompt("enter new user name:", "username");
    if (!newUser)
        return;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', newUser);
    request.open('POST', 'adduser');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_delete_user = function (ix) {
    let username = puser_userList[ix]['addr'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    request.open('POST', 'deleteuser');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_change_user_name = function (ix) {
    let username = puser_userList[ix]['addr'];
    let realname = document.getElementById('puser-obj-realname-' + ix).value;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    formData.append('realname', realname);
    request.open('POST', 'setrealusername');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_change_user_password = function (ix) {
    prompt_password(function (password) {
        let username = puser_userList[ix]['addr'];
        var request = new XMLHttpRequest();
        let formData = new FormData();
        formData.append('addr', puser_orgAddr);
        formData.append('username', username);
        formData.append('password', password);
        request.open('POST', 'setuserpassword');  // FIX_ME
        request.onreadystatechange = function() {
            if (this.readyState === 4) {
                if (this.status === 200) {
                    puser_userList = JSON.parse(this.responseText);
                    puser_display_user_list(puser_userList);
                }
                else {
                    alert(this.responseText);
                }
            }
        };
        request.send(formData);
    });
};

puser_on_change_user_admin = function (ix) {
    let username = puser_userList[ix]['addr'];
    let admin = document.getElementById('puser-obj-admin-' + ix).checked;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    formData.append('admin', admin);
    request.open('POST', 'setuseradmin');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_change_user_create = function (ix) {
    let username = puser_userList[ix]['addr'];
    let create = document.getElementById('puser-obj-create-' + ix).checked;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    formData.append('create', create);
    request.open('POST', 'setusercreate');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_change_user_copy = function (ix) {
    let username = puser_userList[ix]['addr'];
    let copy = document.getElementById('puser-obj-copy-' + ix).checked;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    formData.append('copy', copy);
    request.open('POST', 'setusercopy');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_change_user_conceal = function (ix) {
    let username = puser_userList[ix]['addr'];
    let conceal = document.getElementById('puser-obj-conceal-' + ix).checked;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    formData.append('conceal', conceal);
    request.open('POST', 'setuserconceal');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

puser_on_change_user_delete = function (ix) {
    let username = puser_userList[ix]['addr'];
    let deleteStatus = document.getElementById('puser-obj-delete-' + ix).checked;
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', puser_orgAddr);
    formData.append('username', username);
    formData.append('delete', deleteStatus);
    request.open('POST', 'setuserdelete');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

// --- Loader ---

puser_fetch_user_list = function () {
    var request = new XMLHttpRequest();
    request.open('GET', 'getuserlist?addr=' + puser_orgAddr);
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                puser_userList = JSON.parse(this.responseText);
                puser_display_user_list(puser_userList);
            }
            else {
                alert("No connection with the blockchain network");
                window.close();
            }
        }
    };
    request.send();
};

puser_display_page5 = function(addr) {
    puser_orgAddr = addr;
    document.getElementById("body").innerHTML = pageUsers;
    document.getElementById("puser-obj-target").innerText = addr;
    document.getElementById('vdiv0').style.display = "none";
    puser_fetch_user_list();
};
