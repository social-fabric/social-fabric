/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let pageConsole =
    '<div class="p-vdiv-all">\n' +
    '   <div class="p-hdiv-top">\n' +
    '      <label class="p-obj-title" ><h1>Blockchain Component Deployment</h1></label>\n' +
    '      <label class="p-help-link" onclick="window.open(\'docs/index.html\', \'_blank\')">help and documentation</label>\n' +
    '   </div>\n' +
    '   <div id="pco-hdiv-middle">\n' +
    '      <div id="pco-log-area"></div>\n' +
    '   </div>\n' +
    '   <div class="p-hdiv-bottom">\n' +
    '      <button id="pco-obj-button-abort" onclick="pco_on_deploy_abort()" >Abort</button>\n' +
    '   </div>\n' +
    '</div>';

var pco_log_text = '';
var pco_ret_func = null;

pco_on_deploy_abort = function () {
    window.clearInterval(g_logTimer);
    if (pco_ret_func)
        pco_ret_func();
    pco_ret_func = null;
};

pco_fetch_next_deploy = function () {
    let consortium = g_bcNodeData['name'];
    var request = new XMLHttpRequest();
    let formData = new FormData();
    formData.append('consortium', consortium);
    request.open('POST', '/deploy');
    request.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                g_bcNodeData = JSON.parse(this.responseText);
                pco_log_text = pco_log_text + g_bcNodeData['msg'];
                let div_log_area = document.getElementById('pco-log-area');
                div_log_area.innerHTML = pco_log_text;
                div_log_area.scrollTo(0,div_log_area.scrollHeight);
                if (g_bcNodeData['errorcode'] === 0) { // exit on first error
                    g_logTimer = window.setTimeout(pco_fetch_next_deploy, 300);
                }
            }
            else if (this.status === 201) {
                let div_log_area = document.getElementById('pco-log-area');
                pco_log_text = pco_log_text + "\nOperation Completed\n";
                div_log_area.innerHTML = pco_log_text;
                div_log_area.scrollTo(0,div_log_area.scrollHeight);
                document.getElementById('pco-obj-button-abort').innerText = "Close";
                document.getElementById("pco-log-area").style.cursor = "default";
            }
            else {
                alert(this.responseText);
                on_abort();
            }
        }
    };
    request.send(formData);
};

display_console = function (ret_func = null) {
    pco_ret_func = ret_func;
    pco_log_text = '';
    document.getElementById("body").innerHTML = pageConsole;
    document.getElementById("pco-log-area").style.cursor = "wait";
};

