const photoswipe = require('photoswipe');
const requiredHTML = require('./required-html.js');

const {Viewer, registerViewer} = require('omnic-viewer-core');
const packageJSON = require('./package.json');

let htmlIncluded = false;

function possiblyIncludeHTML() {
    if (!htmlIncluded) {
        document.body.innerHTML += requiredHTML;
        htmlIncluded = true;
    }
}

class PhotoswipeImageViewer extends Viewer {
    static get types() {
       return packageJSON.omnic.types;
    }

    mount(element) {
        possiblyIncludeHTML();
        console.log('photo on element!');
        element.remove();
    }
}
console.log('photo viewer loading!');

registerViewer(PhotoswipeImageViewer);

console.log('photo viewer loaded!');
