var CodeReorder = (function(){

    function showAnswer(answer) {
        $('#answer').empty();
        $(answer).each(function(idx, line) {
            $('#answer')
                .append($('<li>')
                    .append($('<pre>')
                        .append($('<code>', {'class': 'javascript', 'text': line}))));
        });

        $('pre code').each(function(i, block) {
            hljs.highlightBlock(block);
        });
    }

    function get_grade() {} // placeholder for JS Input

    function get_state() {
        var code = [];
        $('#answer code').each(function(idx, line) {
            code.push($(line).text());
        });

        var state = {'code': code};
        return JSON.stringify({'code': code});
    }

    // Called with the user's previous response to get_state().
    // Because this function is sometimes called prior to document.ready,
    // we set the global value for the answer variable
    function set_state(json) {
        try {
            var state = JSON.parse(json);
            if (state && 'code' in state) {
                var code = state['code'];

                // Show the answer when the page loads
                $(document).ready(function() {
                    showAnswer(code);
                });
            }
        } catch(e) {
            console.error("Error parsing state", e);
        }
    }

    return {
        'get_grade': get_grade,
        'get_state': get_state,
        'set_state': set_state,
    };

}());

$(document).ready(function() {

    $(document).foundation({
        reveal : {
            animation : 'fade'
        }
    });

    // Use syntax highlighting
    hljs.initHighlightingOnLoad();

    // Make the lines of code sortable
    $('.code').sortable()
              .disableSelection();

    var $runningJs = $('#running');
    var $error = $('#error');
    $('#draw').on('click', function() {

        // Remove the exisiting canvas
        var canvasId = $runningJs.attr('data-processing-target');
        $('#'+canvasId).replaceWith($('<canvas>', {'id': canvasId}));

        // Clear any previous errors
        $error.html('');

        // Collect the code text from all the code uls
        var code = '';
        $('.code li').each(function(idx, item) {
            code = code + "\n" + $(item).text();
        });

        $runningJs.html(code);

        try {
            Processing.reload();
        } catch(e) {
            $error.html(e.message);
        }
    });
});
