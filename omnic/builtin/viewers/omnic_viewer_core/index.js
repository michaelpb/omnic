'use strict';

const CanvasViewer = require('./canvas-viewer');

class Viewer {
}


function setup() {
    if (!window.OMNIC) {
        window.OMNIC = {};
    }
    if (!window.OMNIC.viewers) {
        window.OMNIC.viewers = {};
    }
}

function activate(element, viewerClass) {
    const viewer = new viewerClass();
    viewer.mount(element);
}

function registerViewer(viewerClass) {
    setup();
    for (const type of viewerClass.types) {
        window.OMNIC.viewers[type] = element => {
            activate(element, viewerClass);
        };
    }
}

module.exports = {
    Viewer,
    CanvasViewer,
    registerViewer,
};
