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
    window['showHelp'] = function(topic, defaultFirst) {
        var $accordion;
        if (topic) {
            $accordion = $('#help-content .accordion a[href=' + topic + ']');
        }
        if (defaultFirst && (!$accordion || !$accordion.length)) {
            $accordion = $('#help-content .accordion a').first();
        }
        if ($accordion && !$accordion.parent().hasClass('active')) {
            $accordion.trigger('click');
        }
    };
    window['showHelp'](window.location.hash, true);

    // Google search
    $('#artwork-search').on('submit', function() {
        var $form = $(this);
        var site = $form.find('[name=site]').val();
        var q = $form.find('[type=text]').val();
        if (q) {
            var action = $form.find('[name=action]').val();
            action += '?#q=site:' + encodeURIComponent(site + ' ' + q);
            window.open(action, '_blank')
        } else {
            // If no search query, redirect to site home
            window.location = site;
        }
        return false;
    });
});
