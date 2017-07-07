'use strict';

window.OMNIC.registerViewer = (viewerName, viewerClass) => {
    window.OMNIC.viewers[viewerName] = viewerClass;
};
console.log('core viewer loaded!');
