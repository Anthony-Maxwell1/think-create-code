$(document).ready(function() {

    // Attach the Ace editor
    var $code = $('code');
    var $input = $('#id_code');

    var editor = ace.edit($code.get(0));
    editor.setShowFoldWidgets(false);

    var session = editor.getSession();
    session.setMode("ace/mode/javascript");
    session.setUseWorker(false);
    session.setUseSoftTabs(true);
    session.setTabSize(4);

    // Communicate code changes to the input field
    // (have to manually trigger changes to hidden fields)
    editor.on("change", function() {
        $input.val(editor.getValue())
              .trigger('change');
    });

    var $script = $('#script-preview');
    var $autoupdate = $('#autoupdate');
    var $error = $('#error');

    function updateDrawing() {

        // Do nothing unless autoupdate is checked.
        if (!$autoupdate.is(':checked')) {
            return true;
        }

        // 1. Hide any previous errors
        $error.hide();

        var code = $input.val();
        if (code) {

            // 2. Recreate the exisiting canvases
            $('canvas').each(function(idx, item) {
                var $canvas = $(item);
                $canvas.replaceWith($('<canvas>', {'id': $canvas.attr('id')}));
            });

            // 3. Transfer code into script block
            $script.html(code);

            // 4. Try running the script
            try {
                Processing.reload();
            } catch(e) {
                // 5. Show any errors
                $error.html(e.message);
                $error.show();
            }

            // 5. Resize the drawing area
            $(document).foundation('equalizer', 'reflow');
        }

        return true;
    }

    $input.on('change', updateDrawing);
    $autoupdate.on('change', updateDrawing);
});
