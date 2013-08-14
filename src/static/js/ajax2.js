$(document).ready(function () {
	var username  = $('#newUsername');
	username.change(function(){		
		$.ajax({
			url: '/usernameCheck',
			type: "POST",
			data: { what: username.val()},
			dataType: "json",
			success: function (data) {
				if (data == true) {
					$(".controls").addClass("control-group warning");
					username.after("<span class='help-inline'>Username unavailable</span>");
				} else {
					$(".controls").removeClass("control-group warning");
					$(".help-inline").remove();
				}
			}
		})
	});
	var pass = $("#newPassword");
	pass.change(function(){
		if (pass.val().length < 8) {
			$(".controls").addClass("control-group warning");
			pass.after("<span class='help-inline'>Password must be at least 8 characters.</span>");
		} else {
			$(".controls").removeClass("control-group warning");
			$(".help-inline").remove();
		}		
	});
	var confirm = $("#confirm");
	confirm.change(function(){
		if (confirm.val() != pass.val() || confirm.val().length < 8) {
			$(".controls").addClass("control-group warning");
			if ( $(".help-inline").text() == "") {
				confirm.after("<span class='help-inline'>Passwords must match</span>");
			}
		} else {
			$(".controls").removeClass("control-group warning");
			$(".help-inline").remove();
		}		
	});
})

