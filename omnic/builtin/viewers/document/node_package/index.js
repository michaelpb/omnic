console.log('document viewer loaded!');

function activate(element) {
    element.innerHTML = '<p>lol</p>';
}

function init() {
    if (!window.OMNIC) window.OMNIC = {};
    if (!window.OMNIC.viewers) window.OMNIC.viewers = {};

    window.OMNIC.viewers['PDF'] = activate;
    window.OMNIC.viewers['application/pdf'] = activate;
}

init()
