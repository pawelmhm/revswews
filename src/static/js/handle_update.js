(function () {
	var oldForm = $('#singleReviewRequest'),
		activateEdit = $('#updater');

	var getForm = new XMLHttpRequest();

	activateEdit.click(function () { 
		console.log("click");
		var content = $('.content'),
			title = $('.title').text(),
			category = $('.category').text(),
			deadline = $('.deadline').text();

		// create a new form append to div
		var updatedRequest = new FormData();
	    var fields = ["title","content","category","deadline"];
	    for (i=0;i< fields.length;i++) {
		// if there is something new here - update
			    updatedRequest.append(fields[i],newContent);
	    }
	    console.log(updatedRequest)
	    /* var oReq = new XMLHttpRequest();
	    oReq.open("POST","/req/update/"); //get value of id)
	    oReq.send(updatedRequest); */
	})


})();