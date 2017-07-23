'use strict';

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
    const viewer = viewerClass();
    viewer.mount(element);
}

function registerViewer(viewerClass) {
    console.log('register viewer!');
    setup();
    for (const type of viewerClass.types) {
        console.log('hi', type, viewerClass);
        window.OMNIC.viewers[type] = element => {
            activate(element, viewerClass);
        };
    }
}

module.exports = {
    Viewer,
    registerViewer,
};
