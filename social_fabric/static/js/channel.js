/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let pageChannel = ''
    + '<div id="vdiv0">\n'
    + '</div>\n'
    + '<div class="p-vdiv-all">\n'
    + '   <div class="p-hdiv-top">\n'
    + '      <h1><label class="p-obj-title" >Blockchain Channel List</label></h1>\n'
    + '      <label class="p-help-link" onclick="window.open(\'docs/index.html\', \'_blank\')">help and documentation</label>\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-middle">\n'
    + '      <div>'
    + '         <button id="pch-obj-export-orderer"  onclick="pch_on_export_orderer()" >Export&nbsp;Orderer</button>\n'
    + '         <button id="pch-obj-export-organization"  onclick="pch_on_export_organization()" >Export&nbsp;Organization</button>\n'
    + '      </div>'
    + '      <div>'
    + '         <button id="pch-obj-create-channel"  onclick="pch_on_create_channel()" >Create&nbsp;Channel</button>\n'
    + '         <button id="pch-obj-attach-channel"  onclick="pch_on_join_channel()" >Join&nbsp;Channel</button>\n'
    + '      </div>'
    + '   </div>\n'
    + '   <div id="pch-channel-list-header" >'
    + '       <label id="pch-obj-label-channel" >Channel</label>\n'
    + '       <label id="pch-obj-label-org" >Organization</label>\n'
    + '       <button class="pch-obj-hidden-button-add-org" >Add&nbsp;Organization</button>\n'
    + '   </div>\n'
    + '   <div id="pch-channel-list">\n'
    + '   </div>\n'
    + '   <div class="p-hdiv-bottom">\n'
    + '      <button id="pch-obj-button-close"  onclick="pch_on_close_page3()" >Close</button>\n'
    + '   </div>\n'
    + '   <a id="pch-hidden-link"></a>'
    + '   <input type="file" id="pch-hidden-file-input"/>'
    + '</div>\n';

pch_display_channel_list = function(aList) {
    let htmlList = document.getElementById("pch-channel-list");
    while (htmlList.firstChild)
        htmlList.removeChild(htmlList.firstChild);
    for (ix = 0; ix < aList.length; ix++) {
        let buttonClass = 'pch-obj-hidden-button-add-org';
        if (aList[ix]['channel']) {
            buttonClass = 'pch-obj-button-add-org';
        }
        let div = document.createElement("div");
        div.className = "pch-channel-list-row";
        div.innerHTML = '<label class="pch-obj-channel">' + aList[ix]['channel'] + '</label>'
                      + '<label class="pch-obj-org">' + aList[ix]['org'] + '</label>'
                      + '<button class=' + buttonClass + ' onclick="pch_on_add_org(' + ix + ')" >Add&nbsp;Organization</button>';
        htmlList.appendChild(div);
    }
    document.getElementById('vdiv0').style.display = "none";
};

var pch_channel_list = [];

// --- Events ---

pch_on_create_channel = function () {
    let channelName = window.prompt("enter a channel name");
    if (!channelName)
        return;
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('channelname', channelName);
    request.open('POST', 'createchannel');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
            }
            else {
                alert(this.responseText);
                pch_display_page_channel();
            }
        }
    };
    request.send(formData);
    document.getElementById('vdiv0').style.display = "block";
    display_console(pch_display_page_channel);
};

pch_on_export_orderer = function () {
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    request.open('POST', 'exportorderer');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                document.getElementById('vdiv0').style.display = "none";
                const url = window.URL.createObjectURL(new Blob([this.responseText], {type: 'text/plain'}));
                const aLink = document.getElementById('pch-hidden-link');
                aLink.href = url;
                aLink.download = 'orderer-connection.json';
                aLink.click();
                window.URL.revokeObjectURL(url);
            }
            else {
                alert(this.responseText);
                pch_display_page_channel();
            }
        }
    };
    request.send(formData);
    document.getElementById('vdiv0').style.display = "block";
};

pch_on_export_organization = function () {
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    request.open('POST', 'exportorganization');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                document.getElementById('vdiv0').style.display = "none";
                const url = window.URL.createObjectURL(new Blob([this.responseText], {type: 'text/plain'}));
                const aLink = document.getElementById('pch-hidden-link');
                aLink.href = url;
                aLink.download = 'organization-config.json';
                aLink.click();
                window.URL.revokeObjectURL(url);
            }
            else {
                alert(this.responseText);
                pch_display_page_channel();
            }
        }
    };
    request.send(formData);
    document.getElementById('vdiv0').style.display = "block";
};

pch_on_join_channel = function () {
    let channelName = window.prompt("enter a channel name");
    if (!channelName)
        return;
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    formData.append('channelname', channelName);
    request.open('POST', 'joinchannel');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
            }
            else {
                alert(this.responseText);
                pch_display_page_channel();
            }
        }
    };
    request.send(formData);
    document.getElementById('vdiv0').style.display = "block";
    display_console(pch_display_page_channel);
};


pch_on_close_page3 = function () {
   pc_display_page1();
};

pch_on_add_org = function (ix) {

    let fileInput = document.getElementById('pch-hidden-file-input');
    fileInput.onchange = function (event) {
        let file = event.target.files[0];
        let reader = new FileReader();
        reader.onload = function(e) {

            console.log(e.target.result);

            let consortium = g_bcNodeData['name'];
            let channel = pch_channel_list[ix]['channel'];
            var request = new XMLHttpRequest();
            let formData = new FormData();
            formData.append('consortium', consortium);
            formData.append('channel', channel);
            formData.append('filecontent', e.target.result);
            request.open('POST', 'addorgtochannel');
            request.onreadystatechange = function() {
                if (this.readyState === 4) {
                    if (this.status === 200) {
                        g_bcNodeData = JSON.parse(this.responseText);
                        g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
                    }
                    else {
                        alert(this.responseText);
                        pch_display_page_channel();
                    }
                }
            };
            request.send(formData);
        };
        reader.readAsText(file);
        display_console(pch_display_page_channel);
    };
    fileInput.click();
};

// --- Loader ---

pch_refresh_channel_list = function () {
    var request = new XMLHttpRequest();
    request.open('GET', 'getchannellist');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                pch_channel_list = JSON.parse(this.responseText);
                pch_display_channel_list(pch_channel_list);
            }
            else {
                document.getElementById('vdiv0').style.display = "none";
                alert("No connection with the blockchain network");
                window.close();
            }
        }
    };
    request.send();
    document.getElementById('vdiv0').style.display = "block";
};

pch_display_page_channel = function() {
    document.getElementById("body").innerHTML = pageChannel;
    pch_refresh_channel_list();
};
