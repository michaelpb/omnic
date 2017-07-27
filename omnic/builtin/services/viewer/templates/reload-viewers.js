{% extends "iffy.js" %}

{% block body %}

if (!window.OMNIC) window.OMNIC = {};
if (!window.OMNIC.viewers) window.OMNIC.viewers = {};

var TIMEOUT = 15000; // check after 15 seconds
var BUNDLE_URL = '{{ viewer_bundle_url }}';

function checkIfPageHasViewers() {
    var elements = document.querySelectorAll('[omnic-viewer]');
    if (elements.length < 1) {
        return false;
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

var viewersExist = checkIfPageHasViewers();
if (viewersExist) {
    loadViewerBundle();
}
{% endblock body %}
