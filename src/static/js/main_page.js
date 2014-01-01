$(document).ready(function(){
	$('#login').click(function() {
		$('#myModal').modal({
			keyboard: false
		});
	})
    var article = $('.request-title');
	article.hover(function(event){            
		options = {
			animation:true,
		};
	})
    
    // update pagination depending on 
    // the page where visitor is
    var prev = $('#previous'),
        next = $('#next');
    if (prev.length == 0 || next.length == 0) return false;
    var locale = window.location.href.split('/');
    var previousPage = locale[locale.length-1] - 1;
    if (previousPage >= 0) {
         prev.attr('href',previousPage);
    } 
    var nextPage = Number(locale[locale.length-1]) + 1
    if (nextPage <= next.parents()[1].children.length - 3) {
        next.attr('href',nextPage);
    }
})
