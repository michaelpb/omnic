const jsc3d = require('jsc3d');

function activate(element) {
    console.log('activating!');
}

window.OMNIC.viewers['STL'] = activate;
window.OMNIC.viewers['OBJ'] = activate;
console.log('document viewer loaded!');
