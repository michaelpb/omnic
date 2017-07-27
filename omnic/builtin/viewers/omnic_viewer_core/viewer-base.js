'use strict';

class Viewer {
    static get css() {
        return ''; // Override to get CSS info
    }

    static mountPage(doc) {
        const selector = this.types
            .map(type => `[omnic-viewer="${type}"]`)
            .join(', ');

        const elements = doc.querySelectorAll(selector);

        for (const element of elements) {
            this.prepElement(element);
        }
    }

    static prepElement(element) {
        element.addEventListener('click', () => {
            if (!element._omnic_instance) {
                element._omnic_instance = new this();
            }
            const instance = element._omnic_instance;
            const src = element.getAttribute('omnic-viewer-src');
            instance.mount(element, src);
        });
    }

}

module.exports = Viewer;
