'use strict';

const {omnicViewerNames} = require('./package.json');

// Activate all viewers
{% for viewer_name in viewer_names %}
    {
        const viewerModule = require('{{ viewer_name }}');
        if (viewerModule.init) {
            viewerModule.init({});
        }
    }
{% endfor %}


