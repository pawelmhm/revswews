(function () {
    var editRequest = $('.edit_request'),
	    oldRequest = $('.request_review'),
		activateEdit = $('#updater'),
		cancel = $('#cancel'),
		reqSingle = $('.req-single'),
		activateReview  = $('#activateReview');
    
    editRequest.hide();
    reqSingle.hide();
	
	activateEdit.click(function () { 
	    editRequest.toggle('slow');
	    oldRequest.hide('slow');
	    cancel.click(function(e){
	        editRequest.hide();
	        oldRequest.show('slow');
	        e.preventDefault()	;        
	    })
	})
	
	activateEdit.submit(function (e) {
	    e.preventDefault()
	    return false;
	})
   
	 activateReview.click(function() {
	     reqSingle.toggle();
	 })
})();