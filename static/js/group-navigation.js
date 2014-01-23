$(document).ready(function(){
	showFirstPara();
	$("#createGroup").click(function(){
		$(".groupDynamic").fadeOut();
		$(".createGroup").fadeIn();
	});
	$("#createGroupBack").click(function(){
		$(".createGroup").fadeOut();
		$(".groupDynamic").fadeIn();		
	});
	$("#createGroupSend").click(function(){
		document.getElementById("createGroupItem").submit();
	});
});

function isCreateGroupPublic(){
	if ($("#createPublicGroup").prop('checked')) {
		return true;
	};
	return false;
}

function showFirstPara(){
	$(".groupDynamicBrief").each(function(){
        $(this).children().hide();
        $(this).children().eq(0).show();
    });
}