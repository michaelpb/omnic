// const pdfjs = require('pdfjs-dist');
// "pdfjs-dist": "1.8.507"
// TODO: need to add a worker build system for the viewers

function activate(element) {
    console.log('activating!');
    element.innerHTML = '<p>lol</p>';
}

window.OMNIC.viewers['PDF'] = activate;
window.OMNIC.viewers['application/pdf'] = activate;
console.log('document viewer loaded!');
