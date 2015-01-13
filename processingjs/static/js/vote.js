$(document).ready(function() {

    // Hook up reload button
    $('#page-reload').on('click', function() {
        window.location.reload();
    });

    // Hook up the like/unlike buttons
    $('#artwork-list-content').delegate('a.post-vote', 'click', function(evt) {
        var $target = $(evt.currentTarget);
        var post_url;

        var diff = 0;
        if ($target.hasClass('like')) {
            post_url = $target.attr('like-url');
            $target.removeClass('like')
                   .addClass('unlike')
                   .attr('title', 'unlike');
            diff = 1;
        } else if ($target.hasClass('unlike')) {
            post_url = $target.attr('unlike-url');
            $target.removeClass('unlike')
                   .addClass('like')
                   .attr('title', 'like');
            diff = -1;
        }

        if (post_url) {
            $.ajax({
                url: post_url,
                method: 'POST',
                success: function() {
                    var $score = $target.find('.artwork-score');
                    $score.text(Number($score.text()) + diff);
                },
                error: function() {
                    console.error(arguments);
                    $('#reveal-modal-error').click();
                }
            });
        }

        return false;
    });
});
