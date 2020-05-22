/*
 Copyright (c) 2020 - Neptunium Inc.

 SPDX-License-Identifier: Apache-2.0
 */

let popup = ''
    + '<div id="pup-div-center">\n'
    + '   <div id="pup-div-left">\n'
    + '      <label id="pup-label-password" >Password:</label>\n'
    + '      <label id="pup-label-confirm" >Confirm:</label>\n'
    + '   </div>\n'
    + '   <div id="pup-div-right">\n'
    + '      <input type="password" id="pup-obj-password" />\n'
    + '      <input type="password" id="pup-obj-confirm" />\n'
    + '      <label id="pup-obj-error" ></label>\n'
    + '      <div class="pup-div-bottom">\n'
    + '         <button id="pup-button-ok"  onclick="on_popup_ok()" >Ok</button>\n'
    + '         <button id="pup-button-cancel"  onclick="on_popup_cancel()" >Cancel</button>\n'
    + '      </div>\n'
    + '   </div>\n'
    + '</div>\n';

var popup_return = null;

on_popup_close = function (password) {
   document.body.removeChild(document.body.childNodes[0]);
   document.getElementsByClassName('p-vdiv-all')[0].style.opacity = '1.0';
   g_popup_active = false;
   if (popup_return)
       popup_return(password)
};

on_popup_cancel = function () {
    popup_password = null;
    on_popup_close(null);
};

on_popup_ok = function () {
    let password = document.getElementById('pup-obj-password').value;
    let confirm  = document.getElementById('pup-obj-confirm').value;
    if (password === confirm) {
        on_popup_close(password);
    }
    else {
        document.getElementById('pup-obj-password').value = '';
        document.getElementById('pup-obj-confirm').value = '';
        document.getElementById('pup-obj-error').innerText = 'Passwords differ, please re-enter';
        document.getElementById("pup-obj-password").focus();
    }
};

on_popup_next_field = function(event) {
    if (event.keyCode === 13)
        document.getElementById("pup-obj-confirm").focus();
};

on_popup_key_down = function(event) {
    if (event.keyCode === 13)
        on_popup_ok();
};

prompt_password = function (on_prompt_return) {
    g_popup_active = true;
    popup_password = null;
    popup_return = on_prompt_return;
    let popupDiv = document.createElement('div');
    popupDiv.className = "popup-div";
    popupDiv.innerHTML = popup;
    let previous = document.getElementsByClassName('p-vdiv-all')[0];
    previous.style.opacity = '0.5';
    document.body.insertBefore(popupDiv, document.body.childNodes[0]);
    document.getElementById("pup-obj-confirm").addEventListener('keydown', on_popup_key_down);
    document.getElementById("pup-obj-password").addEventListener('keydown', on_popup_next_field);
    document.getElementById("pup-obj-password").focus();
};

