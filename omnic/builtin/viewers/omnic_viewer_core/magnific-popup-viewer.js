
const Viewer = require('./viewer-base');
const $ = require('jquery');
window.$ = $;
const magnificPopup = require('magnific-popup');
// const magnificPopupStyle = require('magnific-popup/dist/magnific-popup.css');

// Until we have a CSS build system:
const magnificPopupStyle = require('./magnific-popup-hack.css');

class MagnificPopupViewer extends Viewer {
    static get css() {
        return magnificPopupStyle;
    }

    static get magnificType() {
        return 'inline';
    }

    render() {
        return '<strong>Replace me!</strong>';
    }

    mount(element, source) {
        const popupHTML = this.render(element, source);
        console.log('mounting!', popupHTML);
        $.magnificPopup.open({
            items: {
                src: popupHTML,
            },
            type: this.magnificType,
        });
    }
}

module.exports = MagnificPopupViewer;
