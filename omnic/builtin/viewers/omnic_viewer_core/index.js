'use strict';
const insertCss = require('insert-css');

const Viewer = require('./viewer-base');
const CanvasViewer = require('./canvas-viewer');
const MagnificPopupViewer = require('./magnific-popup-viewer');


function registerViewer(viewerClass) {
    insertCss(viewerClass.css || '');
    viewerClass.mountPage(document);
}

module.exports = {
    Viewer,
    MagnificPopupViewer,
    CanvasViewer,
    registerViewer,
};
