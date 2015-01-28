$(document).ready(function() {
    $('.uofa-code-editor-widget').each(function(idx, wrapper) {
        var $wrapper = $(wrapper);
        var $code = $wrapper.find('code');
        var $input = $wrapper.find('input[type=hidden]');

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
    });
});
