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
            callFunc("drawIframe"+artworkId, code);
        }
        // Disable animation if #autoupdate unchecked.
        else {
            callFunc("animateIframe"+artworkId, false);
        }
    }

    function callFunc(func, arg) {
        if (func in window) {
            window[func](arg);
        } else {
            console.error("Error: " + func + " does not exist");
        }
    }

    editor.on("change", updateDrawing);
    $autoupdate.on('change', updateDrawing);

    // If there's code in the input field, but none in the editor, then populate it
    if ($input.length && $input.val()) {
        editor.setValue($input.val(), -1);
    }
});
