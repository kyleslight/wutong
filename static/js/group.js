var isLoginBox=false;
var isRegisterBox=false;
var isOtherOptionShow=false;
var activeIndex=-1;
var elapseTime = 4500;
var shortElapseTime=4000;
var _showwel_flag = true;
var userInfo=[{"userName":"","userId":0}];
var groupInfo=[{"groupName":"","groupId":0}];
var groupUserInfo=[{"is_leader":false,"is_subleader":false,"is_member":false,"join_time":null}];

// TODO: refactor, package as a function. this statement should run at first
location.pathname;
match = "/g/\d+";
var url = "ws://" + location.host + location.pathname + "/message";
console.log(url);
var msg_socket = new WebSocket(url);
msg_socket.onclose = function() {};

// get group unsync information
unsyncGroup();

$(document).ready(function(){
    //check sex of the member
    renderMaleAndFemale();
    var groupMottoPrimaryWidth=$("#groupMotto").width();
    if(groupMottoPrimaryWidth>425){
            $("#groupMotto").css({"margin-top":"2px"});
    }

    // join group
    $("#publicJoin").click(function(){
    	$.ajax({
			url:location.pathname + "/groupJoin",
			type:"POST",
			dataType:"json",
			data:{
				uid:userInfo[0].userId,
				gid:groupInfo[0].groupId
			},
			success:function(data){
	        	alert("You have joined this group");
	        	$(".groupPrompt").slideUp();
			}
		});
    	return false;
    })
    $("#privateJoin").click(function(){
    	// contact the group leader

    })

    $("#topic236Title").click(function(){
        alert(1);
        var topicId=$(this).attr("id");
        return false;
    });

    // groupItem
    $(".groupOptions a").click(function(){
        if (_showwel_flag == true){
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, shortElapseTime);
            checkIsOtherOptionShow();
            var indexOfDetailItem=$(".groupOptions a").index($(this));
            switch(indexOfDetailItem){
            	case(0):unsyncGroupBulletin();break;
            }
            if (isOtherOptionShow) {
                $("#groupOptionShow"+activeIndex).removeClass("active").addClass("outOfView");
                $("#groupOptionShow"+activeIndex).animate({left:"-960px"},1500,function(){
                    $(this).slideUp(400);
                    $("#groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").show(function(){
                        var prepareHeight=$(this).height()+25+"px";
                        $(".groupItem").animate({height:prepareHeight},1000,function(){
                            $("#groupOptionShow"+activeIndex).addClass("none");
                        });
                        $("#groupOptionShow"+indexOfDetailItem).animate({left:"0px"},1000,function(){
                            $(this).removeClass("prepare").addClass("active");
                            $(".groupItem").css("height","auto");
                        });
                    });

                });
            }else{
                $("#groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").show(function(){
                    $(".groupItem").slideDown(500,function(){
                        $("#groupOptionShow"+indexOfDetailItem).removeClass("prepare").addClass("active").animate({left:'0px'},1500);
                    });
                });
            }
            return false;
        }
    })
    // group item back
    $(".optionBack").click(function(){
        var indexOfOptionBack=$(".optionBack").index($(this));
        $("#groupOptionShow"+indexOfOptionBack).removeClass("active").addClass("outOfView");
        $("#groupOptionShow"+indexOfOptionBack).animate({left:"-960px"},1500,function(){
            $(".groupItem").slideUp(500,function(){
                $("#groupOptionShow"+indexOfOptionBack).removeClass("outOfView").hide();
            });
            $(".bulletinCon").fadeOut(500);
            // isOtherOptionShow=false;
        });
        for (var i = 0; i < $(".groupOptions a").length; i++) {
            $("#groupOptionShow"+i).removeClass("active");
        };
        return false;
    })
    // bulletin content show
    $(".bulletinInline").click(function(){
        var indexOfbulletinInline=$(".bulletinInline").index($(this));
        if($(this).next().css("display")=="none"){
            $(this).next().fadeIn(1000);
        }
        else{
            $(this).next().fadeOut(500);
        }
        return false;
    })
    // member card effect
    $("div.memberCard").mouseover(function(){
        $(this).css({"background-color":"#680","color":"white","cursor":"pointer"});
        $(this).click(function(){
            if ($(this).children("div.memberDetail").css("display")=="none") {
                $(this).css("cursor","default");
                $(this).children("div.memberDetail").slideDown(150).css({"position":"absolute","z-index":"999999","top":"72px","opacity":"0.9"});
            }
        })
        return false;
    })
    $("div.memberCard").mouseleave(function(){
        $(this).children("div.memberDetail").slideUp(50);
        $(this).css({"background-color":"rgba(255,255,255,0.5)","color":"black"});
        return false;
    })
    // change send state
    $("#changeSendState").click(function(){
        if ($(".topicSend").css("display")=="none") {
            $(".chatSend").slideUp(500,function(){
                $(".topicSend").slideDown(1000);
                $("#changeSendState").html("切换至聊天模式");
            });
        }else{
            $(".topicSend").slideUp(1000,function(){
                $(".chatSend").slideDown(500);
                $("#changeSendState").html("切换至话题模式");
            });
        }
        return false;
    })

    // submit communication data
    var chatCon;
    $("#chatSubmitButton").click(function(){
        submitChatData();
        return false;
    });
    $("#topicSubmitButton").click(function(){
        submitTopicData();
        return false;
    });
    $("#expandChatSubmitButton").click(function(){
    	submitExpandChatData();
    	return false;
    })
    //for quick submit
    $(window).keyup(function(e){
        var keyCode=e.keyCode;
        if (keyCode==13&&event.ctrlKey==1) {
            if ($(".topicSend").css("display")=="none") {
                submitChatData();
            }else{
                submitTopicData();
            }
        }
        return false;
    });
    // $(window.frames["ueditor_0"]).find("body.view").keyup(function(e){
    //     alert(1);
    //     var keyCode=e.keyCode;
    //     if (keyCode==13&&event.ctrlKey==1){
    //         submitTopicData();
    //     }
    // })

    function removeMessage() {
        var thedata=$("#communication").children().size();
        if (thedata>30) {
            for (var i = 30; i < thedata; i++) {
                $("#communication").children("li").eq(i).remove();
            }
        }
    }

    msg_socket.onmessage = function(e) {
        var data = e.data;
        var item;
        if (data)
            item = JSON.parse(data);
        else
            return;
        // test userImage
        var homeUrl="http://localhost:8888/static/css/image/";
        var userImageUrl;
        switch(item.user.uid){
        	case 0:userImageUrl=homeUrl+"test11.jpg";break;
        	case 1:userImageUrl=homeUrl+"test12.png";break;
        	case 2:userImageUrl=homeUrl+"test1.png";break;
        	case 3:userImageUrl=homeUrl+"test.png";break;
        	default:userImageUrl=homeUrl+"test7.jpg";break;
    	}
        item.submit_time = item.submit_time.toString().substring(5,19);
        if (!item.title) {
	        // TODO: 通过title判断是否为topic
	        var condata = '<li id="topic_'+item.id+'" class="chat">'
	                    + 	'<a class="userImage" href="#"><img src="'+item.user.avatar+'"/></a>'
	                    + 	'<div class="talkMain">'
	                    + 		'<a class="userName" href="#">'+item.user.penname+'</a>'
	                    + 		'<div class="timeShow">'+item.submit_time+"</div>"
	                    + 		'<div class="talkContent">'+item.content+'</div>'
	                    +	'</div>'
	                    +'</li>';

	        $("#communication").prepend(condata);
	        removeMessage();
	    }else{
            tempTopicContent=$("#messageTemp").html(item.content).eq(0).children().eq(0);
	    	var condata = '<li id="topic_'+item.id+'" class="topicOutter">'
	                    // + '<a class="userImage" href="#"><img src="'+item.user.avatar+'"/></a>'
	                    + '<a class="userImage" href="#"><img src='+userImageUrl+'/></a>'
	                    + '<div class="talkMain"><div class="talkAction">'
	                    + '<a class="userName" href="#">'+item.user.penname+'</a> 发起了话题 '
	                    + '<a href="javascript:void(0)" id="topic'+item.id+'Title" class="talkTitle" onclick="clickTopicTitle('+item.id+')" >'+item.title+'</a></div>'
	                    + "<div class='timeShow'>"+item.submit_time+"</div>"
	                    + "<div class='topicTalkContent'>"+tempTopicContent.html().toString()+"</div></div></li>";
	        $("#communication").prepend(condata);
	        removeMessage();
	    }
    }

});

function unsyncGroup(){
	// get group infomation
	$.ajax({
		url:location.pathname+"/groupInfo",
		type: "GET",
		dataType:"json",
		async: false,
		success:function(data){
			groupInfo[0].groupName = data.name;
			groupInfo[0].groupId = data.gid;
			if(data.publicity){
				$(".groupPromptPrivate").css({"display":"none"});
				$("#contactGroupLeader").css({"display":"none"});
			}else{
				$(".groupPromptPublic").css({"display":"none"});
			}
			$('#groupTitleName').text(groupInfo[0].groupName);
		}
	});
	// get group-user infomation
	$.ajax({
		url:location.pathname+"/groupUserInfo",
		type: "POST",
		dataType:"json",
		async: false,
		data:{
			uid:userInfo[0].userId,
			gid:groupInfo[0].groupId
		},
		success:function(data){
			if(data.is_member){
				$(".groupPrompt").css({"display":"none"});
			}
		}
	});
}

function unsyncGroupBulletin(){
	// get group bulletin
	$.ajax({
		url:location.pathname+"/bulletin",
		type: "GET",
		dataType:"json",
		async: false,
		success:function(data){
			console.log(data);
		}
	});
}

// function for submit data
function submitChatData(){
	chatCon=$("#chatData").val();
    if($("#chatData").val().length>1000){
        alert("请保持字数在1000字以内");
        return;
    }
    if(chatCon=="<ex>"){
    	$(".normalChatSend").slideUp(500,function(){
            $(".expandChatSend").slideDown(1000);
        });
        $("#chatData").val("");
        return;
    }
    chatCon=chatCon.replace(/</g,"&lt").replace(/>/g,"&gt");
    chatCon=chatCon.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");
    chatCon=chatCon.httpHtml();
    // alert(chatCon);
    if(chatCon.length==0){
    	$("#communicationData").addClass("littleTremble");
        setTimeout(function(){
    		$("#communicationData").removeClass("littleTremble");
    	},1000);
        // alert("Please input content");
        $("#chatData").val("");
        return;
    }
    if(chatCon.length==0||chatCon.toString().replace(/(\r)*\n/g,"").replace(/\s/g,"").length==0){
        $("#communicationData").addClass("littleTremble");
        setTimeout(function(){
            $("#communicationData").removeClass("littleTremble");
        },1000);
        // alert("Please input content");
        return;
    }
    // var thedata=$(".communication").children().size();
    // if (thedata>30) {
    //     for (var i =30; i < thedata; i++) {
    //         $("#communication").children("li").eq(i).remove();
    //     }
    // }

    $("#chatData").val("");
    // send message to server, TODO: please refactor
    message = {
        "content": chatCon,
    };
    message = JSON.stringify(message);
    msg_socket.send(message);
}

function submitExpandChatData(){
	var expandChatCon=$("#expandChatData").val();
	if(expandChatCon=="<p>&lt;fl&gt;</p>"||expandChatCon=="&lt;fl&gt;"){
		$(".expandChatSend").slideUp(1000,function(){
            $(".normalChatSend").slideDown(500);
        });
        $(window.frames["ueditor_1"].document).find("body.view").html("");
		return;
	}
	if (expandChatCon.length==0) {
        $("#communicationData").addClass("littleTremble");
        setTimeout(function(){
    		$("#communicationData").removeClass("littleTremble");
    	},1000);
        return;
    };

    // send message to server, TODO: please refactor
    message = {
        "content": expandChatCon,
    };
    message = JSON.stringify(message);
    msg_socket.send(message);

    $(window.frames["ueditor_1"].document).find("body.view").html("");
    return false;
}

function submitTopicData(){
	var topicTitle=$('#topicTitle').val();
    var topicCon=$("#topicData").val();
    if (topicCon.length==0||topicTitle.length==0) {
        $("#communicationData").addClass("littleTremble");
        setTimeout(function(){
    		$("#communicationData").removeClass("littleTremble");
    	},1000);
        return;
    };
    message = {
    	option:"send_topic",
    	title:topicTitle,
        content: topicCon,
    };
    message = JSON.stringify(message);
    msg_socket.send(message);

    $(window.frames["ueditor_0"].document).find("body.view").html("");
    $("#topicTitle").val("");
    return false;
}

function checkIsOtherOptionShow(){
    for (var i = 0; i < $(".groupOptions a").length; i++) {
        if ($("#groupOptionShow"+i).hasClass("active")) {
            isOtherOptionShow=true;activeIndex=i;
            return;
        };
    };
    isOtherOptionShow=false;
}

function renderMaleAndFemale(){
    $(".memberSex").each(function(){
        if ($(this).text()=="♂") {
            $(this).css("color","lightblue");
        }else{
            $(this).css("color","pink");
        }
    })
}

function clickTopicTitle(topic_id){
	alert(topic_id);
	$('html,body').animate({scrollTop:0},1000);
	return false;
}

String.prototype.httpHtml = function(){
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}
