$(document).ready(function(){ 
    $(document).foundation();
    $('.artwork.preview, .code-block').resizable({
         start: function(event, ui) {
             $(this).css('pointer-events','none');
         },
         stop: function(event, ui) {
             $(this).css('pointer-events','auto');
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
});
