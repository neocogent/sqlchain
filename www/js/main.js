(function($){
    var id = 0;

    function apiClk(e) {
        var url='', obj = $(this);
        e.stopPropagation();
        if(obj.hasClass('opt'))
            url = obj.text();
        if(obj.is('span')) {
            obj = obj.parent();
            url = obj.text().split('?')[0] + url;
        }
        var objIns = obj.next().hasClass('info') ? obj.next() : obj;
        if($(this).is( 'li' )) {
            if(obj.next().hasClass('info')) 
                obj.next().toggle();
            if(obj.hasClass('noargs'))
                url = obj.text().split('?')[0]
            }
        if(objIns.next().hasClass('resp'))
            objIns.next().remove();
        else {
            $.get(url, function( data ) {
                var msg = $('#blank').clone().attr('id', '#d'+id).insertAfter(objIns);
                msg.html(obj.hasClass('raw') ? data : "<pre>"+JSON.stringify(data, null, 2)+"</pre>");
                id += 1;
                }, "json");
            }
    }
    $(document).ready( function() {
        $('.apiClk li').click(apiClk);
        $('.apiClk span').click(apiClk);
    });
})(jQuery);
