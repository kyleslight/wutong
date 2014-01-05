$(document).ready(function(){
	$("#createGroup").click(function(){
		$(".groupDynamic").fadeOut();
		$(".createGroup").fadeIn();
	});
	$("#createGroupBack").click(function(){
		$(".createGroup").fadeOut();
		$(".groupDynamic").fadeIn();		
	});
	$("#createGroupSend").click(function(){
		var url = location.pathname.slice(0,-9) + '/g/create';
		$.post(url,{
			'name':$("#createGroupName").val(),
			'intro':$("#createGroupIntro").val(),
			'tags':$("#creareGroupTag").val(),
			'is_public':isCreateGroupPublic(),
		},function(data){
			alert('小组"'+$("#createGroupName").val()+'"已成功申请');
			$(".createGroup").fadeOut();
			$(".groupDynamic").fadeIn();
		});
	})
});

function isCreateGroupPublic(){
	if ($("#createPublicGroup").prop('checked')) {
		return true;
	};
	return false;
}