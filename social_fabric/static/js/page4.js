/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let page4 = ''
    + '<div id="vdiv0">\n'
    + '</div>\n'
    + '<div class="p-vdiv-all">\n'
    + '   <div class="p-hdiv-top">\n'
    + '      <h1><label class="p-obj-title" >Blockchain Add Owner</label></h1>\n'
    + '      <label class="p-help-link" onclick="window.open(\'docs/html/index.html\', \'_blank\')">help and documentation</label>\n'
    + '   </div>\n'
    + '   <div id="p4-hdiv-middle">\n'
    + '      <div id="p4-vdiv-left">\n'
    + '            <button id="p4-obj-import-cert"  onclick="p4_on_import_x509_certificate()" >Import<br>X.509<br>Certificate</button>\n'
    + '      </div>\n'
    + '      <div class="p4-vdiv-center-left">\n'
    + '         <b><label id="p4-obj-label-org" >Organization</label></b>\n'
    + '         <b><label id="p4-obj-label-country" >Country</label></b>\n'
    + '         <b><label id="p4-obj-label-state" >State or Province</label></b>\n'
    + '         <b><label id="p4-obj-label-locality" >Locality</label></b>\n'
    + '         <b><label id="p4-obj-label-addr" >DNS Domain</label></b>\n'
    + '         <b><label id="p4-obj-label-catype" >CA Type</label></b>\n'
    + '         <b><label id="p4-obj-label-caroot" >CA Root</label></b>\n'
    + '      </div>\n'
    + '      <div class="p4-vdiv-center-right">\n'
    + '         <input id="p4-obj-org" />\n'
    + '         <input id="p4-obj-country" />\n'
    + '         <input id="p4-obj-state" />\n'
    + '         <input id="p4-obj-locality" />\n'
    + '         <input id="p4-obj-addr" />\n'
    + '         <input id="p4-obj-catype" readonly />\n'
    + '         <input id="p4-obj-caroot" readonly />\n'
    + '      </div>\n'
    + '      <div id="p4-vdiv-right">\n'
    + '         <div id="p4-hdiv-right">\n'
    + '            <button id="p4-obj-generate-cert"  onclick="p4_on_generate_x509_certificate()" >Generate<br>X.509<br>Certificate</button>\n'
    + '         </div>\n'
    + '      </div>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-bottom">\n'
    + '         <button id="p4-obj-button-cancel"  onclick="p4_on_close_page4()" >Close</button>\n'
    + '   </div>\n'
    + '</div>\n';

// --- Loader ---

p4_refresh_add_owner = function (param, freeze=false) {
    document.getElementById("body").innerHTML = page4;
    document.getElementById("p4-obj-org").value = addOwner['org'];
    document.getElementById("p4-obj-country").value = addOwner['country'];
    document.getElementById("p4-obj-state").value = addOwner['state'];
    document.getElementById("p4-obj-locality").value = addOwner['locality'];
    document.getElementById("p4-obj-addr").value = addOwner['addr'];
    document.getElementById("p4-obj-catype").value = addOwner['catype'];
    document.getElementById("p4-obj-caroot").value = addOwner['caroot'];
    if (freeze) {
       document.getElementById("p4-obj-org").readonly = true;
       document.getElementById("p4-obj-addr").readonly = true;
    }
    document.getElementById('vdiv0').style.display = "none";
};

// --- Events ---

p4_on_generate_x509_certificate = function () {
    let org = document.getElementById("p4-obj-org").value;
    let country = document.getElementById("p4-obj-country").value;
    let state = document.getElementById("p4-obj-state").value;
    let locality = document.getElementById("p4-obj-locality").value;
    let addr = document.getElementById("p4-obj-addr").value;
    if (!org) {
       alert('Organization must have a value to generate a certificate');
       return;
    }
    if (!addr) {
       alert('DNS Domain must have a value to generate a certificate');
       return;
    }
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('org', org);
    formData.append('country', country);
    formData.append('state', state);
    formData.append('locality', locality);
    formData.append('addr', addr);
    request.open('POST', 'genownercert');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                addOwner = JSON.parse(this.responseText);
                p4_refresh_add_owner(addOwner, true);
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

p4_on_import_x509_certificate = function () {
    let org = document.getElementById("p4-obj-org").value;
    let country = document.getElementById("p4-obj-country").value;
    let state = document.getElementById("p4-obj-state").value;
    let locality = document.getElementById("p4-obj-locality").value;
    let addr = document.getElementById("p4-obj-addr").value;
    var xhr = new XMLHttpRequest();
    let formData = new FormData();
    let fileInput = document.createElement("input");
    fileInput.setAttribute("type", "file");
    fileInput.name = 'file';
    fileInput.id = 'uploadField';
    fileInput.style.display = 'none';
    fileInput.onchange = function () {
        formData.append('org', org);
        formData.append('country', country);
        formData.append('state', state);
        formData.append('locality', locality);
        formData.append('addr', addr);
        formData.append('file', fileInput.files[0]);
        xhr.open("POST", '/importownercert', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    addOwner = JSON.parse(this.responseText);
                    p4_refresh_add_owner(addOwner, true);
                }
                else {
                    document.getElementById('vdiv0').style.display = "none";
                }
                let elem = document.getElementById('uploadField');
                elem.parentNode.remodeChild(elem);
            }
        };
        document.getElementById('vdiv0').style.display = "block";
        xhr.send(formData);
    };
    document.getElementById('body').appendChild(fileInput);
    fileInput.click();
};

p4_on_close_page4 = function () {
   p3_display_page3();
};

