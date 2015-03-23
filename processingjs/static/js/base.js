$(document).ready(function(){ 
    $(document).foundation({
        reveal : {
            animation : 'fade'
        }
    });
    $('.artwork.preview, .code-block').resizable({
         start: function(event, ui) {
             $(this).css('pointer-events','none');
         },
         stop: function(event, ui) {
             $(this).css('pointer-events','auto');
         },
         resize: function(event, ui) {
            var $code = $('code');
            if ($code.length && ('ace' in window)) {
                var editor = ace.edit($code.get(0));
                editor.resize();
            }
         }
     }).find('.ui-icon-gripsmall-diagonal-se')
     // Replace small grip icon with large grip
       .removeClass('ui-icon-gripsmall-diagonal-se')
       .addClass('ui-icon-grip-diagonal-se');

    // Make share-link's selectable on click
    $('.share-link').on('click', function() {
        var textC = $(this).get(0);
        if (document.selection)
        {
            //Portion for IE
            var div = document.body.createTextRange();
            div.moveToElementText(textC);
            div.select();
        }
        else
        {
            //Portion for FF
            var div = document.createRange();
            div.setStartBefore(textC);
            div.setEndAfter(textC);
            window.getSelection().addRange(div);
        }
    });

    // Hide/show help accordion according to #hash
    var hash = window.location.hash;
    var $accordion;
    if (hash) {
        $accordion = $('#help-content .accordion a[href=' + hash + ']');
    }
    if (!$accordion || !$accordion.length) {
        $accordion = $('#help-content .accordion a').first();
    }
    $accordion.trigger('click');
});
