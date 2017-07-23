// const pdfjs = require('pdfjs-dist');
// "pdfjs-dist": "1.8.507"

const {Viewer, registerViewer} = require('omnic-viewer-core');
const packageJSON = require('./package.json');

class PDFViewer extends Viewer {
    static get types() {
       return packageJSON.omnic.types;
    }

    mount(element) {
        console.log('mounting on element!');
        element.remove();
    }
}
console.log('document viewer loading!');

registerViewer(PDFViewer);

console.log('document viewer loaded!');
