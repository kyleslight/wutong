$(document).ready(function(){
	$(".content p").each(function(){
		if ($(this).html()=="<br>") {
			$(this).height(10);
		};
	})

	$(".content p").mouseover(function(){
  		$(this).addClass("turnToBlue");

	});
	$(".content p").mouseout(function(){
  		$(this).removeClass("turnToBlue");
	});
})


