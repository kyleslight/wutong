$(document).ready(function(){
	showFirstPara();
	$(window).scroll(function(){
		scrollLoading(".groupDynamic");
	});
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
			'public_level': getPublicLevel(),
		},function(data){
			var err = getError(data);
			if (err) {return;}
			return;
			// TODO
			var gid = data.gid;
			showError("小组"+$("#createGroupName").val()+"已成功申请<br>5秒后将自动跳转到新创建的小组<br>若跳转失败，请点击以下链接<br><a href='/g/"+data+"'>"+$("#createGroupName").val()+"</a>",20000);
			setTimeout(function(){
				self.location='/g/'+data;
			},5000);
		});
	});
});

function getPublicLevel(){
	if ($("#createPublicGroup").prop('checked')) {
		return 'public';
	};
	return 'private';
}

function showFirstPara(){
	$(".groupDynamicBrief").each(function(){
        $(this).children().hide();
        $(this).children().eq(0).show();
    });
}
