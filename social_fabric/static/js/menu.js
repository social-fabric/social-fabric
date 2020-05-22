/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let menu_page = ''
    + '<div class="p-vdiv-all">\n'
    + '   <div class="p-hdiv-top">\n'
    + '      <label class="p-obj-title" ><h1>Blockchain Component Administration</h1></label>\n'
    + '      <label class="p-help-link" onclick="window.open(\'docs/html/index.html\', \'_blank\')">help and documentation</label>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-middle">\n'
    + '      <h2><label id="pmenu-obj-title">Please, select an operation:</label></h2>'
    + '      <label id="pmenu-obj-dummy"></label>'
    + '   </div>\n'
    + '   <div id="pmenu-hdiv-middle">\n'
    + '      <div id="pmenu-vdiv-left">\n'
    + '         <button class="pmenu-button" id="pmenu-button-create-example" onclick="on_menu_create_network_example()" >Create a Network from an Example</button>\n'
    + '         <button class="pmenu-button" id="pmenu-button-create" onclick="on_menu_create_network()" >Create a Network</button>\n'
    + '         <button class="pmenu-button" id="pmenu-button-attach" onclick="on_menu_attach_org()" >Attach an Organization to an Existing Network</button>\n'
    + '         <button class="pmenu-button" id="pmenu-button-password" onclick="on_menu_change_password()" >Change Admin Password</button>\n'
    + '      </div>\n'
    + '      <div id="pmenu-vdiv-right">\n'
    + '      </div>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-bottom">\n'
    + '      <button id="pmenu-button-next"  onclick="on_menu_next()" hidden >Proceed</button>\n'
    + '   </div>\n'
    + '</div>\n';

let menu_create = ''
    + '      <div class="pmenu-vdiv-right-left">\n'
    + '         <label class="pmenu-right-label" id="pm-create-obj-name-label" >Consortium Name</label>\n'
    + '         <label class="pmenu-right-label" id="pm-create-obj-addr-label" >Consortium Address</label>\n'
    + '      </div>\n'
    + '      <div class="pmenu-vdiv-right-right">\n'
    + '         <input class="pmenu-right-obj" id="pm-create-obj-name" />\n'
    + '         <input class="pmenu-right-obj" id="pm-create-obj-addr" />\n'
    + '      </div>\n';

let menu_attach = ''
    + '      <div class="pmenu-vdiv-right-left">\n'
    + '         <button id="pm-hidden-button-import-orderer" >Import Orderer Connection</button>\n'
    + '         <label class="pmenu-right-label" id="pm-create-consortium-name-label" >Consortium Name</label>\n'
    + '         <label class="pmenu-right-label" id="pm-create-consortium-addr-label" >Consortium Address</label>\n'
    + '         <label class="pmenu-right-label" id="pm-attach-orderer-name-label" >Orderer Name</label>\n'
    + '         <label class="pmenu-right-label" id="pm-attach-orderer-addr-label" >Orderer Address</label>\n'
    + '         <label class="pmenu-right-label" id="pm-attach-orderer-port-label" >Orderer Port Number</label>\n'
    + '         <label class="pmenu-right-label" id="pm-attach-orderer-cert-label" >Orderer TLS Certificate</label>\n'
    + '      </div>\n'
    + '      <div class="pmenu-vdiv-right-right">\n'
    + '         <button id="pm-button-import-orderer" onclick="on_menu_import_orderer_conn()" >Import Orderer Connection</button>\n'
    + '         <input class="pmenu-right-obj" id="pm-attach-consortium-name" />\n'
    + '         <input class="pmenu-right-obj" id="pm-attach-consortium-addr" />\n'
    + '         <input class="pmenu-right-obj" id="pm-attach-orderer-name" />\n'
    + '         <input class="pmenu-right-obj" id="pm-attach-orderer-addr" />\n'
    + '         <input class="pmenu-right-obj" id="pm-attach-orderer-port" />\n'
    + '         <textarea class="pmenu-right-obj" id="pm-attach-orderer-cert" ></textarea>\n'
    + '         <input type="file" id="pm-attach-file-input" hidden />\n'
    + '      </div>\n';

let menu_password = ''
    + '      <div class="pmenu-vdiv-right-left">\n'
    + '         <label class="pmenu-right-label" id="pm-passwd-obj-old-label" >Old Password</label>\n'
    + '         <label class="pmenu-right-label" id="pm-passwd-obj-new-label" >New Password</label>\n'
    + '         <label class="pmenu-right-label" id="pm-passwd-obj-confirm-label" >Confirm Password</label>\n'
    + '      </div>\n'
    + '      <div class="pmenu-vdiv-right-right">\n'
    + '         <input type="password" class="pmenu-right-obj" id="pm-passwd-old" />\n'
    + '         <input type="password" class="pmenu-right-obj" id="pm-passwd-new" />\n'
    + '         <input type="password" class="pmenu-right-obj" id="pm-passwd-confirm" />\n'
    + '      </div>\n';


// FIX_ME: Should be css styles in globals.css
menu_set_button = function (id) {
    document.getElementById(id).style.color = 'black';
    document.getElementById(id).style.backgroundColor = 'white';
    document.getElementById(id).onmouseenter = null;
    document.getElementById(id).onmouseleave = null;
};

// FIX_ME: Should be css styles in globals.css
menu_reset_button = function (id) {
   document.getElementById(id).style.color = 'white';
   document.getElementById(id).style.backgroundColor = '#0673ba';
   document.getElementById(id).onmouseenter = function () {
       this.style.color = 'black';
       this.style.backgroundColor = 'white';
   };
   document.getElementById(id).onmouseleave = function () {
       this.style.color = 'white';
       this.style.backgroundColor = '#0673ba';
   };
};

// On enter, trigger next button
return_key_event = function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    document.getElementById("pmenu-button-next").click();
  }
};

on_menu_create_network = function () {
    menu_set_button("pmenu-button-create");
    menu_reset_button("pmenu-button-attach");
    menu_reset_button("pmenu-button-password");
    document.getElementById("pmenu-vdiv-right").innerHTML = menu_create;
    document.getElementById("pmenu-button-next").style.display = 'block';
    document.getElementById("pmenu-button-next").onclick = on_menu_create_next;
    document.getElementById("pm-create-obj-name").focus();
    document.getElementById("pm-create-obj-addr").addEventListener("keyup", return_key_event);
};

on_menu_import_orderer_conn = function () {
    let fileInput = document.getElementById('pm-attach-file-input');
    fileInput.onchange = function (event) {
        let file = event.target.files[0];
        let reader = new FileReader();
        reader.onload = function(e) {
            let conn_dict = JSON.parse(e.target.result);
            document.getElementById('pm-attach-consortium-name').value = conn_dict['consortium']['name'];
            document.getElementById('pm-attach-consortium-addr').value = conn_dict['consortium']['addr'];
            document.getElementById('pm-attach-orderer-name').value = conn_dict['orderer']['name'];
            document.getElementById('pm-attach-orderer-addr').value = conn_dict['orderer']['addr'];
            document.getElementById('pm-attach-orderer-port').value = conn_dict['orderer']['port'];
            document.getElementById('pm-attach-orderer-cert').value = conn_dict['orderer']['tlscacerts'].replace(/\\n/g, '\n');
        };
        reader.readAsText(file);
    };
    fileInput.click();
};

on_menu_attach_org = function () {
    menu_reset_button("pmenu-button-create");
    menu_set_button("pmenu-button-attach");
    menu_reset_button("pmenu-button-password");
    document.getElementById("pmenu-vdiv-right").innerHTML = menu_attach;
    document.getElementById("pmenu-button-next").style.display = 'block';
    document.getElementById("pmenu-button-next").onclick = on_menu_attach_next;
    document.getElementById("pm-attach-consortium-name").focus();
};

on_menu_change_password = function () {
    menu_reset_button("pmenu-button-create");
    menu_reset_button("pmenu-button-attach");
    menu_set_button("pmenu-button-password");
    document.getElementById("pmenu-vdiv-right").innerHTML = menu_password;
    document.getElementById("pmenu-button-next").style.display = 'block';
    document.getElementById("pmenu-button-next").onclick = on_menu_password_next;
    document.getElementById("pm-passwd-old").focus();
    document.getElementById("pm-passwd-confirm").addEventListener("keyup", return_key_event);
};

on_menu_create_network_example = function () {
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('workingmode', 'CreateWithExample');
    request.open('POST', 'setworkingmode');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_workingMode = this.responseText;
                pc_fetch_node_list();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

on_menu_create_next = function () {
    let consortiumName = document.getElementById("pm-create-obj-name").value;
    if (!consortiumName) {
        alert("A Consortium Name is Required");
        return;
    }
    let consortiumAddr = document.getElementById("pm-create-obj-addr").value;
    if (!consortiumAddr) {
        alert("A Consortium Address is Required");
        return;
    }
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('workingmode', 'Create');
    formData.append('consortiumname', consortiumName);
    formData.append('consortiumaddr', consortiumAddr);
    request.open('POST', 'setworkingmode');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_workingMode = this.responseText;
                pc_fetch_node_list();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

on_menu_attach_next = function () {
    let consortiumName = document.getElementById("pm-attach-consortium-name").value;
    let consortiumAddr = document.getElementById("pm-attach-consortium-addr").value;
    if (!consortiumAddr) {
        alert("A Consortium Address is Required");
        return;
    }
    let ordererName = document.getElementById("pm-attach-orderer-name").value;
    if (!ordererName) {
        alert("A Consortium Owner is Required");
        return;
    }
    let ordererAddr = document.getElementById("pm-attach-orderer-addr").value;
    if (!ordererAddr) {
        alert("An Orderer Address is Required");
        return;
    }
    let ordererPort = document.getElementById("pm-attach-orderer-port").value;
    if (!ordererPort) {
        alert("An Orderer Port is Required");
        return;
    }
    let ordererCert = document.getElementById("pm-attach-orderer-cert").value;
    if (!ordererCert) {
        alert("An Orderer TLS Certificate is Required");
        return;
    }
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('workingmode', 'Attach');
    formData.append('consortiumname', consortiumName);
    formData.append('consortiumaddr', consortiumAddr);
    formData.append('orderername', ordererName);
    formData.append('ordereraddr', ordererAddr);
    formData.append('ordererport', ordererPort);
    formData.append('orderercert', ordererCert);
    request.open('POST', 'setworkingmode');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_workingMode = this.responseText;
                pc_fetch_node_list();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

on_menu_password_next = function () {
    let oldPass = document.getElementById("pm-passwd-old").value;
    if (!oldPass) {
        alert('Please, provide previous password');
        return;
    }
    let newPass = document.getElementById("pm-passwd-new").value;
    if (!newPass) {
        alert('Please, provide passwords');
        document.getElementById("pm-passwd-old").value = "";
        return;
    }
    let confPass = document.getElementById("pm-passwd-confirm").value;
    if (newPass !== confPass) {
        alert('New password and confirmation password are different, please re-enter passwords');
        document.getElementById("pm-passwd-old").value = "";
        document.getElementById("pm-passwd-new").value = "";
        document.getElementById("pm-passwd-confirm").value = "";
        return;
    }
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('oldpass', oldPass);
    formData.append('newpass', newPass);
    request.open('POST', 'changeadminpassword');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert("password changed");
                display_menu_page();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

display_menu_page = function () {
    document.getElementById("body").innerHTML = menu_page;
};

on_load_menu_page = function () {
    var request = new XMLHttpRequest();
    let formData = new FormData();
    request.open('GET', 'getworkingmode');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_workingMode = this.responseText;
                if (g_workingMode)
                    pc_fetch_node_list();
                else
                    display_menu_page();
            }
            else {
                alert(this.responseText);
            }
        }
    };
    request.send(formData);
};

