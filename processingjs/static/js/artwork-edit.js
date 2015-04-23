$(document).ready(function() {

    // Attach the Ace editor
    var $code = $('code');
    var $input = $('#id_code');
    var $artwork = $('.artwork');
    var artworkId = $('.artwork').attr('id');
    artworkId = artworkId.replace(/^artwork-/, '');

    var editor = ace.edit($code.get(0));
    editor.setShowFoldWidgets(false);
    editor.$blockScrolling = Infinity;

    var session = editor.getSession();
    session.setMode("ace/mode/javascript");
    session.setUseWorker(false);
    session.setUseSoftTabs(true);
    session.setTabSize(4);

    var $play = $('#play');
    var $pause = $('#pause');

    // Register for the start/stop Animation events, so we get triggered even
    // when the "paused" overlay is clicked.
    $(window).on('artwork.update.animate', function(evt, msg) {
        if (msg['pk'] == artworkId) {
            if (msg['animate']) {
                $play.addClass('disabled');
                $play.prop('disabled', true);
                $pause.removeClass('disabled');
                $pause.prop('disabled', false);
            } else {
                $pause.addClass('disabled');
                $pause.prop('disabled', true);
                $play.removeClass('disabled');
                $play.prop('disabled', false);
            }
        }
    });

    // Call a function with the given name (and implied arguments list)
    // Log error to console if the function does not exist.
    function callFunc(func) {
        if (func in window) {
            window[func].apply(null, Array.prototype.slice.call(arguments, 1));
        } else {
            console.error("Error: " + func + " does not exist");
        }
    }

    function updateDrawing() {
        var code = editor.getValue() || '';
        if ($input.length) {
            $input.val(code);
        }

        // Update the animation code
        callFunc("updateArtwork"+artworkId, {'code': code});
    }

    editor.on("change", updateDrawing);

    $play.on('click', function() {
        callFunc("updateArtwork"+artworkId, {'animate': true});
    });
    $pause.on('click', function() {
        callFunc("updateArtwork"+artworkId, {'animate': false});
    });

    // ADX-133 re-set the editor value to fix issue with HTML element encoding.
    {
        var code = editor.getValue();

        // If there's code in the input field, but none in the editor, use that
        // code instead.
        if ($input.length && $input.val()) {
            code = $input.val();
        } 
        editor.setValue(code, -1);
    }
});
