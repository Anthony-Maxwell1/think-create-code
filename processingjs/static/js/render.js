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

            // 0. Verify the pk
            var $rendered = $('#artwork-rendered');
            var pk = $rendered.attr('pk') || '';

            if (evt && evt.data && evt.data.pk == pk) {
            
                if ('code' in evt.data) {

                    // 1. Show the rendered div
                    $rendered.show();

                    // 2. Recreate the exisiting canvas
                    $('canvas').each(function(idx, item) {
                        var $canvas = $(item);
                        $canvas.replaceWith($('<canvas>', {'id': $canvas.attr('id')}));
                    });

                    // 2. Set the script contents, decoding escaped html as text
                    var tmp = $('<div/>', { 'html' : evt.data.code });
                    $('#script-preview').html(tmp.text());

                    // 3. Listen for canvas resize, and send new size to parent
                    $('#canvas-preview').resize(function() {
                        var $this = $(this);
                        var data = {
                            'width': $this.width(),
                            'height': $this.height()
                        };
                        parent.postMessage({'resize': data, 'pk': pk}, '*');
                    });

                    // 4. Try running the script, sending any errors to parent
                    try {
                        Processing.reload();
                    } catch(e) {
                        parent.postMessage({'error': e.message, 'pk': pk}, '*');
                        // have to re-throw the error, to pass integration tests 
                        throw e;
                    }
                }
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
