$(document).ready(function(){
	$('#login').click(function() {
		$('#myModal').modal({
			keyboard: false
		});
	})
    article = $('.request-title');
	article.hover(function(event){            
		options = {
			animation:true,
		};
		
		$('#example').popover(options)
	})
})