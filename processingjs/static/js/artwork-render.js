// Enable the "Play all" button, if present.
$(document).ready(function() {
    $('#play-all').on('click', function() {
        var $button = $(this);
        $button.prop('disabled', true);
        $button.addClass('disabled');
        $('.paused a').trigger('click');
    });
});

// Create and populate the iframe, and functions that let us communicate
// the code and animation state changes to the iframe, and receive
// messages back.
function createArtworkIframe(args) {
    
    var artworkId = args['id'];
    if (!artworkId) artworkId = '';

    var $target = $(args['target']);

    // 1. Listen for messages from the iframe
    var iframeMessage = function(evt) {
        if (evt && evt.data && evt.data.pk == artworkId) {
            if (args['autosize']) {
                // Respond to resize events
                if (evt.data.resize) {
                    var resize = evt.data.resize;
                    $target.css('width', resize.width);
                    $target.css('height', resize.height);

                    // artwork/edit uses equalizer divs, so reflow them on resize.
                    $(document).foundation('equalizer', 'reflow');
                }
            }

            // Respond to errors
            if (evt.data.error) {
                // Show error if there's an element to show it on (e.g. artwork/edit)
                var $error = $('#error-'+artworkId);
                if ($error.get(0)) {
                    $error.html(evt.data.error).show();
                }
            }
        }
    };
    if (window.addEventListener){
        addEventListener("message", iframeMessage, false);
    } else {
        attachEvent("onmessage", iframeMessage);
    }

    // 2. Create and load the iframe
    var $iframe = $('<iframe>', { 
        'sandbox': 'allow-scripts',
        'src': args['renderUrl'],
        'width': '100%',
        'height': '100%',
        'scrolling': 'no'
    });
    $target.html($iframe);

    // 3. Attach a function to 'window' that lets us communicate the code and
    // animation state changes to the iframe.
    // 
    // This function also trigger an artwork.update.animate event when
    // the animation state changes.
    var animate = false;
    var codeChanged = true;
    var artworkCode = args['code'];
    var updateArtwork = function(opts) {

        // Update the given animation state

        // If no code is provided, then use the most recently-sent code.
        // Otherwise, update the code with the provided parameter.
        if ('code' in opts && (opts['code'] != artworkCode)) {
            artworkCode = opts['code'];
            codeChanged = true;
        }

        // If animate is provided, then update the animate field
        var animateChanged = false;
        if ('animate' in opts && (opts['animate'] != animate)) {
            animate = opts['animate'];
            animateChanged = true;
        }

        // Update the code if animation is enabled, or if changed code
        // hasn't been communicated to the iframe yet.
        var animateMessage = { 
            'animate': animate ? true : false,
            'pk': artworkId
        };
        if (animate && codeChanged) {
            codeChanged = false;

            // Send the code as a message to the iframe
            // Note: this also re-starts the animation, if it was paused.
            $iframe.get(0).contentWindow.postMessage({
                'code': artworkCode,
                'pk': artworkId
            }, '*');;

            $(window).trigger('artwork.update.animate', animateMessage);
        }
        else if (animateChanged) {
            $iframe.get(0).contentWindow.postMessage(animateMessage, '*');

            $(window).trigger('artwork.update.animate', animateMessage);
        }
    }
    window['updateArtwork'+artworkId] = updateArtwork;

    // 4. Show the "paused" overlay and play link for existing artwork
    if (args['overlay']) {

        var $overlay = $(args['overlay']);
        var removeOverlay = function(evt, msg) {
            if (!msg || (msg['pk'] == artworkId)) {

                // Remove this handler to prevent infinite triggering..
                $(window).off('artwork.update.animate', removeOverlay);

                // Hide the clicked overlay
                $overlay.fadeOut('fast');

                // Update the animation
                updateArtwork({'animate': true});
            }
        };
        $overlay.show();
        $overlay.on('click', removeOverlay);
        $(window).on('artwork.update.animate', removeOverlay);
    }
}
