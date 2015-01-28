$(document).ready(function(){ 
    $(document).foundation();
    $('.artwork.preview, .code-block, .uofa-code-editor-widget').resizable({
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
});
