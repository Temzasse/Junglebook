$(document).ready(function(){
	var current;
	// change the avatar when user clicks its thumbnail
	$(".avatar").click(function(){
		$(".selected-avatar").removeClass("selected-avatar")
		$(this).addClass("selected-avatar");

		current = $(this).attr("data-avatar");

		$("#current-avatar").removeClass();
		$("#current-avatar").addClass("current-avatar-"+current)

		// update the avatar input field value
		$("input#avatar").val(current);
	});



	$('.sort-wrapper select').on('change', function () {
		var url = "?sort=";
        var sort_param = $(this).val(); // get selected value
		if (sort_param) { // require a URL
		  window.location.href = url+sort_param;
		}
		return false;
    });


    $(function () {
	  $('[data-toggle="tooltip"]').tooltip()
	})

    // hide the flashed message after 2 sec
	setTimeout(function(){
		$(".flashed-messages").slideUp("slow");
	}, 2000);
});