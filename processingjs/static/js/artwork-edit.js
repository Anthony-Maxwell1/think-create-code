$(document).ready(function() {

    var $script = $('#script-preview');
    var $code = $('#id_code');
    var $autoupdate = $('#autoupdate');
    var $error = $('#error');

    function updateDrawing() {

        // Do nothing unless autoupdate is checked.
        if (!$autoupdate.is(':checked')) {
            return true;
        }

        // 1. Hide any previous errors
        $error.hide();

        var code = $code.val();
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

    $code.on('change', updateDrawing);
    $autoupdate.on('change', updateDrawing);
});
