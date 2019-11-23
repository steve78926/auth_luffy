/**
 * Created by Administrator on 2019/8/21.
 */

/* 这种写法没见过  */

(function(jq){
    jq('.multi-menu .title').click(function(){
        $(this).next().toggleClass('hide');
    });
})(jQuery);
