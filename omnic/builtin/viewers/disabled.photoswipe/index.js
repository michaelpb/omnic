'use const';

const PhotoSwipe = require('photoswipe/dist/photoswipe');
const PhotoSwipeUI = require('photoswipe/dist/photoswipe-ui-default');
const requiredHTML = require('./required-html.js');

const {Viewer, registerViewer} = require('omnic-viewer-core');
const packageJSON = require('./package.json');


let htmlIncluded = false;

function possiblyIncludeHTML() {
    if (!htmlIncluded) {
        const div = document.createElement('div');
        div.innerHTML = requiredHTML;
        document.body.appendChild(div);
        htmlIncluded = true;
    }
}

function initGallery() {
    const pswpElement = document.querySelectorAll('.pswp')[0];

    // build items array
    const items = [
        {
            src: 'https://placekitten.com/600/400',
            w: 600,
            h: 400
        },
        {
            src: 'https://placekitten.com/1200/900',
            w: 1200,
            h: 900
        }
    ];

    // define options (if needed)
    const options = {
        // optionName: 'option value'
        // for example:
        index: 0 // start at first slide
    };

    // Initializes and opens PhotoSwipe
    const gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI, items, options);
    gallery.init();
}

class PhotoswipeImageViewer extends Viewer {
    static get types() {
       return packageJSON.omnic.types;
    }

    mount(element) {
        possiblyIncludeHTML();
        console.log('photo on this element:', element);
        initGallery();
    }
}

registerViewer(PhotoswipeImageViewer);

