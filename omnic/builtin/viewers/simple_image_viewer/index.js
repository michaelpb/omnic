'use const';

const {MagnificPopupViewer, registerViewer} = require('omnic-viewer-core');
const packageJSON = require('./package.json');

class SimpleImageViewer extends MagnificPopupViewer {
    static get types() {
       return packageJSON.omnic.types;
    }

    render(element, source) {
        const style = 'width: 100%;';
        return `<img style="${style}" src="${source}" />`;
    }
}

registerViewer(SimpleImageViewer);

