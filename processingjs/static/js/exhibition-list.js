$(document).ready(function() {
    // Move the play-all buttons to under the exhibition detail
    $('.play-all').each(function(idx, item) {
        var $button = $(item);
        var $exhibition = $button.closest('.exhibition');
        $exhibition.find('.exhibition-detail').append($button);
    });
});
