{% extends "iffy.js" %}

{% block body %}
console.log('its a test');
console.log('its a test');

var TIMEOUT = 2000; // check after 2 seconds

var placeholders = [];
function pushPlaceholder(thumb) {
    placeholders.push(thumb);
    if (_timeout === null) {
        // ensure a timeout has been set
        _timeout = setTimeout(reloadPlaceholders, TIMEOUT);
    }
}

var _timeout = null;

function reloadPlaceholders() {
    for (var i = 0; i < placeholders.length; i++) {
        var thumb = placeholders[i];
        var src = thumb.src;
        src += '&ignore-viewercache=' + new Date().getTime();
        thumb.src = src;
    }
    placeholders = []; // clear placeholders
}

function onLoad(thumb) {
    // NOTE: naturalHeight/naturalWidth is unsupported in IE8
    if (thumb.naturalHeight === 1 && thumb.naturalWidth === 1) {
        console.log('found a placeholder!');
        pushPlaceholder(thumb);
    } else {
        console.log('nope not placeholder!');
    }
}

var thumbs = document.querySelectorAll('img[omnic-thumb]');
var len = thumbs.length;

for (var i=0; i < len; i++) {
    var thumb = thumbs[i];
    if (thumb.complete) {
        onLoad(thumb);
        (function () {
            var firstTrigger = true;
            thumb.addEventListener('load', function () {
                if (firstTrigger) {
                    firstTrigger = false;
                } else {
                    onLoad(thumb);
                }
            });
        })();
    } else {
        thumb.addEventListener('load', function () {
            onLoad(thumb);
        });
    }
}

{% endblock body %}
