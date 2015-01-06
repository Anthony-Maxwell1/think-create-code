$(document).ready(function() {

    var $script = $('#script-preview');
    var $code = $('#id_code');
    var $error = $('#error');

    $('#draw').on('click', function() {

        // 1. Clear any previous errors
        $error.html('');

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
            }
        }

        return false;
    });
});
