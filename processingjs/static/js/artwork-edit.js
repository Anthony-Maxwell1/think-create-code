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

    var $autoupdate = $('#autoupdate');
    function updateDrawing() {
        var code = editor.getValue() || '';
        if ($input.length) {
            $input.val(code);
        }

        // Redraw the iframe if #autoupdate is checked.
        if ($autoupdate.is(':checked')) {
            var func = "drawIframe" + artworkId;
            if (func in window) {
                window[func](code);
            } else {
                console.error("Error updating artwork: " + func + " does not exist");
            }
        }
        // Disable animation if #autoupdate unchecked.
        else {
            window["animateIframe" + artworkId](false);
            var func = "animateIframe" + artworkId;
            if (func in window) {
                window[func](false);
            } else {
                console.error("Error disabling animation: " + func + " does not exist");
            }
        }
    }

    editor.on("change", updateDrawing);
    $autoupdate.on('change', updateDrawing);
});
