(function () {
    var editRequest = $('.edit_request'),
	    oldRequest = $('.request_review'),
		activateEdit = $('#updater'),
		cancel = $('#cancel'),
		reqSingle = $('.req-single'),
		activateReview  = $('#activateReview'),
		updateRequest = $('#updateRequest'),
		oldRequestA = document.getElementsByClassName('request_review')[0];
    
    editRequest.hide();
    reqSingle.hide();
	
	activateEdit.click(function () { 
	    oldRequest.fadeOut('fast',function(){
    	    editRequest.fadeIn('slow');
    	    
    	    cancel.click(function(e){
    	        editRequest.fadeOut('fast',function(){
        	        oldRequest.fadeIn('slow');  
    	        }) 
    	        e.preventDefault()	;     
    	    })
	    })
	})
	
	activateEdit.submit(function (e) {
	    e.preventDefault()
	    return false;
	})
   
	 activateReview.click(function() {
	     reqSingle.toggle('slow');
	 })
	 	 
	 updateRequest.click(function(e){
	     e.preventDefault();
	     formS = new FormData(document.forms["do_update"]);
	     request = new XMLHttpRequest();
	     request.addEventListener('load',function() {
	         if (this.status == 200) {
	             editRequest.fadeOut('fast',function(){
	                 updateOldRequest(document.forms["do_update"]);
        	         oldRequest.fadeIn('slow');  
    	        }) 
	         } else {
	             console.log("error",this.response,this.status);
	         }
	     })
	     // get article id from url
	     locale = window.location.href.split('/');
         articleId = locale[locale.length-1];
	     request.open("POST","http://localhost:5000/req/update/" + articleId)
	     request.send(formS);
	 });
	 
	 function updateOldRequest(formdata) {
	     var z = document.getElementsByClassName("title")[0];
	     for (i=0;i<4;i++){ 
	         for (j=0;j<oldRequestA.childElementCount;j++){
	             currentChild = oldRequestA.children[j];
	             if (document.forms["do_update"][i].id == currentChild.className){
	                 while(currentChild.firstChild) {
	                     currentChild.removeChild(currentChild.firstChild);
	                 }
	                 currentChild.appendChild(document.createTextNode(document.forms["do_update"][i].value));
	             }
	         }
	     }
	 } 
	 $( "#datepicker" ).datepicker();
})();