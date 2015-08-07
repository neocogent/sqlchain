(function($){
    var id = 0;

    function apiClk(e) {
        var url = $(this);
        if(url.next().hasClass('resp'))
            url.next().remove();
        else
            $.get(url.text().split('[')[0], function( data ) {
                var msg = $('#blank').clone().attr('id', '#d'+id).insertAfter(url);
                msg.html(url.hasClass('raw') ? data : "<pre>"+JSON.stringify(data, null, 2)+"</pre>");
                id += 1;
                }, "json");       
    }

    $(document).ready( function() {
        $('.apiClk li').click(apiClk);
    });
})(jQuery);
