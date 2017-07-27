'use const';

const {MagnificPopupViewer, registerViewer} = require('omnic-viewer-core');
const packageJSON = require('./package.json');

class SimplePDFEmbeddedViewer extends MagnificPopupViewer {
    static get types() {
       return packageJSON.omnic.types;
    }

    render(element, source) {
        const {innerHeight, innerWidth} = window;
        const height = innerHeight;
        const width = innerWidth * 0.85;
        const marginLeft = Math.floor((innerWidth - width) / 2);
        return `
            <object data="${source}"
                    type="application/pdf" width="${width}" height="${height}"
                    style="margin-left: %{marginLeft}px;">
                <p><b>Whoops</b>: This browser does not support PDFs. Please
                download the PDF to view it: <a href="${source}">Download PDF</a>.</p>
            </object>
        `;
    }
}

registerViewer(SimplePDFEmbeddedViewer);

