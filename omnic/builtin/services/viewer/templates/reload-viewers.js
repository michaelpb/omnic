{% extends "iffy.js" %}

{% block body %}
var TIMEOUT = 15000; // check after 15 seconds
var BUNDLE_URL = '{{ viewer_bundle_url }}';

function attachClickEventsToViewers() {
    var viewers = document.querySelectorAll('img[omnic-viewer]');
    if (viewers.length < 1) {
        return false;
    }

    for (var i=0; i < viewers.length; i++) {
        var viewer = viewers[i];
        (function (viewer) {
            viewer.addEventListener('click', function () {
                activateViewer(viewer);
            });
        })(viewer)
    }
    return true;
}

function addScript(src) {
    var s = document.createElement('script');
    s.setAttribute('src', src);
    document.body.appendChild(s);
}

function loadViewerBundle() {
    if (!window._OMNIC_VIEWER_BUNDLE_IS_LOADED) {
        addScript(BUNDLE_URL); // need browser cache busting here
        setTimeout(loadViewerBundle, TIMEOUT)
    }
}

var viewersExist = attachClickEventsToViewers();
if (viewersExist) {
    loadViewerBundle();
}
{% endblock body %}
