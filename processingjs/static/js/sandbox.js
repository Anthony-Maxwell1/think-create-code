$(document).ready(function() {

    var editor = ace.edit($('code').get(0));
    editor.setShowFoldWidgets(false);
    editor.$blockScrolling = Infinity;

    var session = editor.getSession();
    session.setMode("ace/mode/javascript");
    session.setUseWorker(false);
    session.setUseSoftTabs(true);
    session.setTabSize(4);

    var $play = $('#play');
    var $pause = $('#pause');
    var $error = $('#error').hide();

    var animate = false;
    var code = $('.code-block').text();
    var codeChanged = false;

    function updateDrawing(opt) {

        var animateChanged = false;
        var $canvas = $('canvas');

        if (opt && 'animate' in opt) {
            if (animate !== opt['animate']) {
                animate = opt['animate'];
                animateChanged = true;
            }
        }

        var _code = editor.getValue() || '';
        if (code !== _code) {
            codeChanged = true;
            code = _code;
        }

        // Update running code
        if (animate && codeChanged) {

            codeChanged = false;

            var $newCanvas = $('<canvas>', {'id': $canvas.attr('id')});
            $canvas.replaceWith($newCanvas);
            $canvas = $newCanvas;

            var tmp = $('<div>', { 'text' : code });
            $('#script-preview').html(tmp.text());

            try {
                $error.empty().hide();
                Processing.reload();
            } catch(e) {
                $error.html(e.message).show();
            }
        }

        // Start/stop animation
        if (animateChanged) {
            var instance = Processing.getInstanceById($canvas.attr('id'));
            if (animate) {
                instance.loop();
            } else {
                instance.noLoop();
            }
        }
    }

    editor.on("change", updateDrawing);

    $play.on('click', function() {
        $play.addClass('disabled');
        $play.prop('disabled', true);
        $pause.removeClass('disabled');
        $pause.prop('disabled', false);

        updateDrawing({'animate': true});
    });
    $pause.on('click', function() {
        $pause.addClass('disabled');
        $pause.prop('disabled', true);
        $play.removeClass('disabled');
        $play.prop('disabled', false);

        updateDrawing({'animate': false});
    });
});
