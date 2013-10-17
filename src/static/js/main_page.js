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
		
		$('#example').popover(options)
	})
    
    //update pagination depending on 
    // the page where visitor is
    var prev = $('#previous'),
        next = $('#next');
    var locale = window.location.href.split('/');
    var previousPage = locale[locale.length-1] - 1;
    if (previousPage >= 0) {
         prev.attr('href',previousPage);
    } 
    var nextPage = Number(locale[locale.length-1]) + 1
    console.log(nextPage);
    if (nextPage <= next.parents()[1].children.length - 3) {
        console.log(nextPage)
        next.attr('href',nextPage);
    }
    

})