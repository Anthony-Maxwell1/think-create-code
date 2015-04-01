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

        function onMessage (evt) {

            // 0. Verify the pk
            var $rendered = $('#artwork-rendered');
            var pk = $rendered.attr('pk') || '';
            var $canvas = $('canvas');

            if (evt && evt.data && evt.data.pk == pk) {
            
                var $error = $('#error-' + pk);
                if ('code' in evt.data) {

                    // 1. Show the rendered div
                    $rendered.show();

                    // 2. Recreate the exisiting canvas
                    var $newCanvas = $('<canvas>', {'id': $canvas.attr('id')});
                    $canvas.replaceWith($newCanvas);
                    $canvas = $newCanvas;

                    // 3. Set the script contents, decoding escaped html as text
                    var tmp = $('<div>', { 'text' : evt.data.code });
                    $('#script-preview').html(tmp.text());

                    // 4. Listen for canvas resize, and send new size to parent
                    $canvas.resize(function() {
                        var $this = $(this);
                        var data = {
                            'width': $this.width(),
                            'height': $this.height()
                        };
                        parent.postMessage({'resize': data, 'pk': pk}, '*');
                    });

                    // 5. Try running the script, reporting any errors to the user
                    try {
                        $error.empty().hide();
                        Processing.reload();
                    } catch(e) {
                        parent.postMessage({'error': e.message, 'pk': pk}, '*');
                        $error.html(e.message).show();
                    }
                }
                else if ('animate' in evt.data) {
                    // Stop or start the animation loop
                    var instance = Processing.getInstanceById($canvas.attr('id'));
                    if (evt.data['animate']) {
                        instance.loop();
                    } else {
                        instance.noLoop();
                    }
                }
            } else {
                console.error(evt);
            }
        };

        if (window.addEventListener){
            addEventListener("message", onMessage, false);
        } else {
            attachEvent("onmessage", onMessage);
        }
    }

    // Otherwise, we just show the warning message.
    else {
        $('#artwork-not-rendered').show();
    }
});
