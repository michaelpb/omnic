{% extends "iffy.js" %}

{% block body %}

if (!window.OMNIC) window.OMNIC = {};
if (!window.OMNIC.viewers) window.OMNIC.viewers = {};

var TIMEOUT = 15000; // check after 15 seconds
var BUNDLE_URL = '{{ viewer_bundle_url }}';

function prepElement(element) {
    var viewerType = element.getAttribute('omnic-viewer');
    var activateViewer = window.OMNIC.viewers[viewerType];
    element.addEventListener('click', function () {
        activateViewer(element);
    });
}

function attachClickEventsToViewers() {
    var elements = document.querySelectorAll('img[omnic-viewer]');
    if (elements.length < 1) {
        return false;
    }

    for (var i=0; i < elements.length; i++) {
        var element = elements[i];
        prepElement(element);
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
