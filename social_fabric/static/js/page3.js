/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let page3 = ''
    + '<div id="vdiv0">\n'
    + '</div>\n'
    + '<div class="p-vdiv-all">\n'
    + '   <div class="p-hdiv-top">\n'
    + '      <h1><label class="p-obj-title" >Blockchain Owner List</label></h1>\n'
    + '      <label class="p-help-link" onclick="window.open(\'docs/html/index.html\', \'_blank\')">help and documentation</label>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-middle">\n'
    + '      <h2><label id="p3-obj-owners" ></label></h2>\n'
    + '      <button id="p3-obj-add-owner"  onclick="p3_on_display_add_owner()" >Add Owner</button>\n'
    + '   </div>\n'
    + '   <div id="p3-owner-list-header" >'
    + '       <label id="p3-obj-label-org" >Organization</label>\n'
    + '       <label id="p3-obj-label-addr" >DNS Domain</label>\n'
    + '       <label id="p3-obj-label-passwd" >Password</label>\n'
    + '       <label id="p3-obj-label-ca-type" >CA Type</label>\n'
    + '       <label id="p3-obj-label-ca-root" >CA Root</label>\n'
    + '       <button id="p3-obj-hidden-button-delete" >Delete</button>\n'
    + '   </div>\n'
    + '   <div id="p3-owner-list">\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-bottom">\n'
    + '      <button id="p3-obj-button-close"  onclick="p3_on_close_page3()" >Close</button>\n'
    + '   </div>\n'
    + '</div>\n';

p3_display_owner_list = function(aList) {
    let htmlList = document.getElementById("p3-owner-list");
    while (htmlList.firstChild)
        htmlList.removeChild(htmlList.firstChild);
    for (ix = 0; ix < aList.length; ix++) {
        let div = document.createElement("div");
        div.className = "p3-owner-list-row";
        div.innerHTML = '<label class="p3-obj-org">' + aList[ix]['org'] + '</label>'
                      + '<label class="p3-obj-addr">' + aList[ix]['addr'] + '</label>'
                      + '<label class="p3-obj-password" onclick="p3_on_change_owner_password(' + ix + ')">' + aList[ix]['password'] + '</label>'
                      + '<label class="p3-obj-ca-type">' + aList[ix]['catype'] + '</label>'
                      + '<label class="p3-obj-ca-root">' + aList[ix]['caroot'] + '</label>'
                      //+ '<button class="p3-obj-button-users" onclick="on_edit_users(' + ix + ')" >Users</button>'
                      + '<button class="p3-obj-button-delete" onclick="p3_on_delete_owner(' + ix + ')" >Delete</button>';
        htmlList.appendChild(div);
    }
    document.getElementById('vdiv0').style.display = "none";
};

// --- Events ---

p3_on_display_add_owner = function () {
    addOwner = {'org': '', 'country': '', 'state': '', 'locality': '', 'addr': '', 'catype': '', 'caroot': ''};
    p4_refresh_add_owner(addOwner, true)
};

p3_on_close_page3 = function () {
   pc_display_page1();
};

p3_on_change_owner_password = function (ix) {
    prompt_password(function (password) {
        let addr = g_bcNodeData['owners'][ix]['addr'];
        var request = new XMLHttpRequest();
        let formData = new FormData();
        formData.append('addr', addr);
        formData.append('password', password);
        request.open('POST', 'setownerpassword');
        request.onreadystatechange = function () {
            if (this.readyState === 4) {
                if (this.status === 200) {
                    g_bcNodeData['owners'] = JSON.parse(this.responseText);
                    p3_display_owner_list(g_bcNodeData['owners']);
                } else {
                    document.getElementById('vdiv0').style.display = "none";
                    alert(this.responseText);
                }
            }
        };
        request.send(formData);
        document.getElementById('vdiv0').style.display = "block";
    });
};

p3_on_delete_owner = function (ix) {
    let addr = g_bcNodeData['owners'][ix]['addr'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('addr', addr);
    request.open('POST', 'deleteowner');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData['owners'] = JSON.parse(this.responseText);
                p3_display_owner_list(g_bcNodeData['owners']);
            }
            else {
                document.getElementById('vdiv0').style.display = "none";
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
    document.getElementById('vdiv0').style.display = "block";
};

// --- Loader ---

p3_refresh_owner_list = function (first) {
    var request = new XMLHttpRequest();
    request.open('GET', 'getownerlist');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData['owners'] = JSON.parse(this.responseText);
                if (first && g_bcNodeData['owners'].length === 0) {
                    p4_refresh_add_owner(addOwner)
                }
                else {
                    p3_display_owner_list(g_bcNodeData['owners']);
                }
            }
            else {
                document.getElementById('vdiv0').style.display = "none";
                alert("No connection with the blockchain network");
                window.close();
            }
        }
    };
    request.send();
};

p3_display_page3 = function(first=false) {
    document.getElementById("body").innerHTML = page3;
    p3_refresh_owner_list(first);
};
