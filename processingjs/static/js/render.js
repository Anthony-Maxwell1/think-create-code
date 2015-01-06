// Included by templates/artwork/render.html
function inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        console.warn(e);
        return true;
    }
}

function getCookies() {
    try {
        return document.cookies;
    } catch (e) {
        console.warn(e);
        return null;
    }
}

$(document).ready(function() {

    // If this page was loaded in an iframe,
    // and we're not exposing any cookies, 
    // it's ok to try to load the code.
    if (inIframe() && !getCookies() ) {

        var loadCode = function(evt) {

            if (evt && evt.data && evt.data.code) {

                // Show the rendered div
                $('#artwork-rendered').show();

                // Set the script contents, decoding escaped html as text
                var tmp = $('<div/>', { 'html' : evt.data.code });
                $('#script-preview').html(tmp.text());

                // Listen for canvas resize, and send new size to parent
                $('#canvas-preview').resize(function() {
                    var $this = $(this);
                    var data = {
                        'width': $this.width(),
                        'height': $this.height()
                    };
                    parent.postMessage({'resize': data}, '*');
                });

                // Run processingJS
                Processing.reload();
            } else {
                console.error(evt);
            }
        };

        if (window.addEventListener){
            addEventListener("message", loadCode, false);
        } else {
            attachEvent("onmessage", loadCode);
        }
    }

    // Otherwise, we just show the warning message.
    else {
        $('#artwork-not-rendered').show();
    }
});
