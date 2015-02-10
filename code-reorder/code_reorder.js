function get_grade() {} // placeholder for JS Input

function get_state() {
    var code = [];
    $('#sortable code').each(function(idx, line) {
        code.push($(line).text());
    });

    var state = {'code': code};
    return JSON.stringify({'code': code});
}

// Called with the user's previous response to get_state()
function set_state(json) {
    try {
        var state = JSON.parse(json);
        if (state && 'code' in state) {
            var code = state['code'];
            $('#sortable').empty();
            $(code).each(function(idx, line) {
                $('#sortable')
                    .append($('<li>')
                        .append($('<pre>')
                            .append($('<code>', {'class': 'javascript', 'text': line}))));
            });

            $('pre code').each(function(i, block) {
                hljs.highlightBlock(block);
            });
        }
    } catch(e) {
        console.error("Error parsing state", e);
    }
}


$(document).ready(function() {
    // Use syntax highlighting
    hljs.initHighlightingOnLoad();

    // Make the code sortable
    $( '#sortable' ).sortable()
                    .disableSelection();

    var $runningJs = $('#running');
    var $error = $('#error');
    $('#draw').on('click', function() {

        // Remove the exisiting canvas
        var canvasId = $runningJs.attr('data-processing-target');
        $('#'+canvasId).replaceWith($('<canvas>', {'id': canvasId}));

        // Clear any previous errors
        $error.html('');

        // Collect the code text from the ul
        var code = '';
        $('#sortable li').each(function(idx, item) {
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
