var isLoginBox = false;
var isRegisterBox = false;
var isOtherOptionShow = false;
var activeIndex = -1;
var elapseTime = 4500;
var shortElapseTime = 4000;
var _showwel_flag = true;
var userInfo;
var groupInfo;
var gid = parseInt(location.pathname.slice(3));
var gurl;
var WebSocket = window.WebSocket || window.MozWebSocket;
var msg_socket;
var removeMessage;
// communicationState -1:no foucus 0:chat focus 1:topic focus 2:expand chat focus
var communicationState=-1;

if(location.pathname.slice(0,2)=="/t"){
    gurl=$("#groupTitleName").attr("href");
}else{
    gurl = location.pathname;
};

$(document).ready(function() {
    renderMaleAndFemale();
    var groupMottoPrimaryWidth = $("#groupMotto").width();
    if (groupMottoPrimaryWidth > 425) {
        $("#groupMotto").css({
            "margin-top": "2px"
        });
    }

    // join group
    $("#publicJoin").click(function() {
        console.log(gurl + "/join");
        $.ajax({
            url: gurl + "/join",
            type: "POST",
            success: function(data) {
                showError("你已加入本小组",2500);
                $(".groupPrompt").slideUp();
            }
        });
        return false;
    })
    $("#privateJoin").click(function() {
        // contact the group leader

    })

    // groupItem
    $(".groupOptions a").click(function() {
        if (_showwel_flag == true) {
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, shortElapseTime);
            checkIsOtherOptionShow();
            var indexOfDetailItem = $(".groupOptions a").index($(this));
            switch (indexOfDetailItem) {
                case (0):
                    unsyncGroupBulletin();
                    break;
            }
            if (isOtherOptionShow) {
                $("#groupOptionShow" + activeIndex).removeClass("active").addClass("outOfView");
                $("#groupOptionShow" + activeIndex).animate({
                    left: "-9topicTagList60px"
                }, 1500, function() {
                    $(this).slideUp(400);
                    $("#groupOptionShow" + indexOfDetailItem).addClass("prepare").css("left", "960px").show(function() {
                        var prepareHeight = $(this).height() + 25 + "px";
                        $(".groupItem").animate({
                            height: prepareHeight
                        }, 1000, function() {
                            $("#groupOptionShow" + activeIndex).addClass("none");
                        });
                        $("#groupOptionShow" + indexOfDetailItem).animate({
                            left: "0px"
                        }, 1000, function() {
                            $(this).removeClass("prepare").addClass("active");
                            $(".groupItem").css("height", "auto");
                        });
                    });

                });
            } else {
                $("#groupOptionShow" + indexOfDetailItem).addClass("prepare").css("left", "960px").show(function() {
                    $(".groupItem").slideDown(500, function() {
                        $("#groupOptionShow" + indexOfDetailItem).removeClass("prepare").addClass("active").animate({
                            left: '0px'
                        }, 1500);
                    });
                });
            }
            return false;
        }
    })
    // group item back
    $(".optionBack").click(function() {
        var indexOfOptionBack = $(".optionBack").index($(this));
        $("#groupOptionShow" + indexOfOptionBack).removeClass("active").addClass("outOfView");
        $("#groupOptionShow" + indexOfOptionBack).animate({
            left: "-960px"
        }, 1500, function() {
            $(".groupItem").slideUp(500, function() {
                $("#groupOptionShow" + indexOfOptionBack).removeClass("outOfView").hide();
            });
            $(".bulletinCon").fadeOut(500);
            // isOtherOptionShow=false;
        });
        for (var i = 0; i < $(".groupOptions a").length; i++) {
            $("#groupOptionShow" + i).removeClass("active");
        };
        return false;
    })
    // bulletin content show
    $(".bulletinInline").click(function() {
        var indexOfbulletinInline = $(".bulletinInline").index($(this));
        if ($(this).next().css("display") == "none") {
            $(this).next().fadeIn(1000);
        } else {
            $(this).next().fadeOut(500);
        }
        return false;
    })
    // member card effect
    $("div.memberCard").mouseover(function() {
        $(this).css({
            "background-color": "#680",
            "color": "white",
            "cursor": "pointer"
        });
        $(this).click(function() {
            if ($(this).children("div.memberDetail").css("display") == "none") {
                $(this).css("cursor", "default");
                $(this).children("div.memberDetail").slideDown(150).css({
                    "position": "absolute",
                    "z-index": "999999",
                    "top": "72px",
                    "opacity": "0.9"
                });
            }
        })
        return false;
    })
    $("div.memberCard").mouseleave(function() {
        $(this).children("div.memberDetail").slideUp(50);
        $(this).css({
            "background-color": "rgba(255,255,255,0.5)",
            "color": "black"
        });
        return false;
    })
    $(".groupMemberList").click(function(){
        // $(".groupOption").fadeOut(1);
        $(".selectedMember").removeClass("selectedMember");
        $(this).addClass("selectedMember");
        // newPos=new Object();
        // newPos.left=event.screenX+20;
        // newPos.top=event.clientY+$(window).scrollTop();
        // console.log(newPos);
        // $(".groupOption").offset(newPos);
        // $(".groupOption").show();
        return false;
    });
    $(".groupOption a").click(function(){
        var memAction=$(this).text();
        var selectedMemberName=$(".selectedMember").children(".groupMemberName").text();
        var app='<li class="groupMemActionList">'
                +            '<span class="groupMemberActionName">'+selectedMemberName+'</span> 已添加至 <span class="groupMemActionCon">'
                +memAction
                +           '</span> 列表 <a href="#" class="groupMemActionCacel">取消</a>'
                +        '</li>';
        switch(memAction){
            case "解除小组成员":console.log("a");break;
            case "任命为副组长":console.log("b");break;
            case "罢免副组长":console.log("c");break;
            case "推选该成员为组长":console.log("d");break;
            default:console.log("erroe");break;
        };
        $(".groupMemActionLog").append(app);
        return false;
    });
    $(".groupMemActionLog").on("click",".groupMemActionCacel",function(){
        $(this).parent().remove();
        return false;
    });
    // change send state
    $("#changeSendState").click(function() {
        if ($(".topicSend").css("display") == "none") {
            $(".chatSend").slideUp(500, function() {
                $(".topicSend").slideDown(1000);
                $("#changeSendState").html("切换至聊天模式");
            });
        } else {
            $(".topicSend").slideUp(1000, function() {
                $(".chatSend").slideDown(500);
                $("#changeSendState").html("切换至话题模式");
            });
        }
        return false;
    })

    // submit communication data
    var chatCon;
    $("#chatSubmitButton").click(function() {
        submitChatData();
        return false;
    });
    $("#topicSubmitButton").click(function() {
        submitTopicData();
        return false;
    });
    $("#expandChatSubmitButton").click(function() {
        submitExpandChatData();
        return false;
    });
    //for quick submit
    $("#chatData").bind({
        focus:function(){communicationState=0;},
        blur:function(){communicationState=-1;}
    });
    $(window).keyup(function(e) {
        var keyCode = e.keyCode;
        if (keyCode==13&&e.ctrlKey&&communicationState==0) {
            submitChatData();
        };
        return false;
    });
    
    $(".topicTalkContent img").click(function(){
        var imgUrl=$(this).attr("src");

    });

    $("#collectTopic").click(function(){
        var collectionUrl=location.pathname+"/collection";
        $.post(collectionUrl, function(data){
            console.log(data);
        })
    });

    removeMessage = function () {
        var thedata = $("#communication").children().size();
        if (thedata > 30) {
            for (var i = 30; i < thedata; i++) {
                $("#communication").children("li").eq(i).remove();
            }
        }
    }

    // init ueditor
    editor.ready(function(){
        var insertImageButtom='<a href="javascript:void(0)" id="insertIamge" title="插入图片" onclick="insertImage('+4+')"></a>';
        $("#edui57").find(".edui-for-link").after(insertImageButtom);
    });
    expandEditor.ready(function(){
        // initUeditor(3);
        var insertImageButtom='<a href="javascript:void(0)" id="insertIamge" title="插入图片" onclick="insertImage('+3+')"></a>';
        $("#edui1").find(".edui-for-link").after(insertImageButtom);
    });

    // check premission
    checkGroupPremission();

    showParaFirst();
    connect_message_server();
});

function unsyncGroupBulletin() {
    // get group bulletin
    $.ajax({
        url: location.pathname + "/bulletin",
        type: "GET",
        dataType: "json",
        async: false,
        success: function(data) {}
    });
}

// function for submit data

function submitChatData() {
    chatCon = $("#chatData").val();
    if ($("#chatData").val().length > 1000) {
        showError("请保持字数在1000字以内",2000);
        return;
    };
    if (chatCon == "<ex>") {
        $(".normalChatSend").slideUp(500, function() {
            $(".expandChatSend").slideDown(1000);
        });
        $("#chatData").val("");
        return;
    };
    if (chatCon.length == 0 || chatCon.toString().replace(/(\r)*\n/g, "").replace(/\s/g, "").length == 0) {
        showError("请输入内容",2000);
        $("#communicationData").addClass("littleTremble");
        setTimeout(function() {
            $("#communicationData").removeClass("littleTremble");
        }, 1000);
        return;
    };
    var chatConBr=chatCon.match(/(\r)*\n/g);
    if (chatConBr) {
        if (chatConBr.length>30) {
            showError("刷屏禁止",2000);
            return;
        };
    };
    chatCon=chatCon.replace(/</g,"&lt").replace(/>/g,"&gt");
    chatCon=chatCon.httpHtml();
    chatCon=chatCon.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");

    $("#chatData").val("");
    var chatBox=document.getElementById("chatData");
    chatBox.style.height = "30px";
    // send message to server, TODO: please refactor
    message = {
        "content": chatCon,
    };
    msg_socket.sendJSON(message);
}

function submitExpandChatData() {
    var expandChatCon = $("#expandChatData").val();
    if (expandChatCon == "<p>&lt;fl&gt;</p>" || expandChatCon == "&lt;fl&gt;") {
        $(".expandChatSend").slideUp(1000, function() {
            $(".normalChatSend").slideDown(500);
        });
        $(window.frames["ueditor_1"].document).find("body.view").html("");
        return;
    }
    if (expandChatCon.length == 0) {
        $("#communicationData").addClass("littleTremble");
        setTimeout(function() {
            $("#communicationData").removeClass("littleTremble");
        }, 1000);
        return;
    };

    // send message to server, TODO: please refactor
    message = {
        "content": expandChatCon,
    };
    msg_socket.sendJSON(message);

    // $(window.frames["ueditor_1"].document).find("body.view").html("");
    expandEditor.setContent("");
    return false;
}

function submitTopicData() {
    if(!checkLogin){
        showError("请先登录",2000);
        return false;
    };
    var topicTitle = $('#topicTitle').val();
    var topicCon = $("#topicData").val();
    if (topicTitle.length == 0) {
        showError("请输入话题标题",2000);
        return;
    };
    if (topicCon.length == 0 ) {
        showError("请输入话题内容",2000);
        return;
    };

    message = {
        option: "send_topic",
        title: topicTitle,
        content: topicCon,
    };
    msg_socket.sendJSON(message);

    editor.setContent("");
    $("#topicTitle").val("");
    showParaFirst();
    return false;
}

function checkGroupPremission(){
    if (!checkLogin) {
        showError("请先登录",2000);
        return false;
    };
    var cgpurl;
    if(location.pathname.slice(0,2)=="/t"){
        cgpurl=$("#groupTitleName").attr("href")+"/permission";
    }else{
        cgpurl = location.pathname + "/permission";
    };
    $.post(cgpurl, {'check_permission': 'is_member'}, function(is_member) {
        if (is_member=="true") {
            $(".groupPrompt").hide();
        }else{
            $(".groupPrompt").show();
        }
    });
    $.post(cgpurl, {'check_permission': 'is_public'}, function(is_public) {
        if (is_public=="true"){
            $(".groupPromptPublic").addClass("activePrompt").show();
        }else{
            $(".groupPromptPrivate,#contactGroupLeader").addClass("activePrompt").show();
        }
    });
}

function checkIsOtherOptionShow() {
    for (var i = 0; i < $(".groupOptions a").length; i++) {
        if ($("#groupOptionShow" + i).hasClass("active")) {
            isOtherOptionShow = true;
            activeIndex = i;
            return;
        };
    };
    isOtherOptionShow = false;
}

function renderMaleAndFemale() {
    $(".memberSex").each(function() {
        if ($(this).text() == "♂") {
            $(this).css("color", "lightblue");
        } else {
            $(this).css("color", "pink");
        }
    })
}

function showParaFirst(){
    $(".topicTalkContent").each(function(){
        $(this).children().hide();
        $(this).children().eq(0).show();
    });
}

String.prototype.httpHtml = function() {
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-|:)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}

// ----------------------------------------------------------------------------
// 自适应连接
function connect_message_server() {
    if (WebSocket) {
        console.log('use websocket way to get/send message');
        connect_message_server_use_websocket();
    } else {
        console.log('use ajax way to get/send message');
        connect_message_server_use_ajax();
    }
}

function connect_message_server_use_ajax(first_message) {
    var url = location.pathname + "/message";
    msg_socket = {
        reconnect_time: 1,
        sendJSON: function(obj) {
            $.ajax({
                url: url,
                type: 'POST',
                data: JSON.stringify(obj),
                contentType: "application/json",
                success: function(data) {
                    if (data == 'not login') {
                        if (!checkLogin) {
                            showError("请先登录",2000);
                            return;
                        };
                        showError("若想参与该小组讨论请加入该小组",2500);
                        return;
                    }
                },
                error: function() {
                    console.log('sendJSON error');
                }
            });
        },
        onmessage: function() {
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data) {
                    $("#communication").prepend(data);
                    showParaFirst();
                    removeMessage();
                    msg_socket.reconnect_time = 1;
                    msg_socket.onmessage();
                },
                error: function() {
                    msg_socket.connect_state = 'closed';
                    setTimeout(msg_socket.onmessage, msg_socket.reconnect_time * 1000);
                    if (msg_socket.reconnect_time < 30) {
                        msg_socket.reconnect_time *= 2;
                    }
                }
            });
        },
    };

    msg_socket.onmessage();
    if (first_message) {
        msg_socket.sendJSON(first_message);
    }
}

function connect_message_server_use_websocket() {
    var url = "ws://" + location.host + location.pathname + "/message/websocket";
    WebSocket.reconnect_time = 1;
    msg_socket = new WebSocket(url);
    msg_socket.onopen = socket_onopen;
    msg_socket.onclose = socket_onclose;
    msg_socket.onmessage = socket_onmessage;
    msg_socket.sendJSON = socket_sendJSON;
    // 若3秒后连接不成功, 则切换成ajax方式
    setTimeout(function() {
        if (msg_socket.readyState != msg_socket.OPEN) {
            connect_message_server_use_ajax();
        }
    }, 3000);
}

function socket_onopen() {
    WebSocket.reconnect_time = 1;
}

function socket_onclose() {
    console.log("网络中断, " + WebSocket.reconnect_time + "秒后重新连接");
    setTimeout(connect_message_server_use_websocket, WebSocket.reconnect_time * 1000);
    if (WebSocket.reconnect_time < 30) {
        WebSocket.reconnect_time *= 2;
    }
}

function socket_onmessage(e) {
    var data = e.data;
    if (!data) {
        console.log('websocket onmessage error: ', data);
        return;
    } else if (data == 'not login') {
        if (!checkLogin) {
            showError("请先登录",1000);
            return false;
        };
        showError("若想参与该小组讨论请加入该小组",3000);
        return false;
    } else {
        $("#communication").prepend(data);
        showParaFirst();
        removeMessage();
    }
}

function socket_sendJSON(obj) {
    if (msg_socket.readyState == msg_socket.OPEN) {
        var data = JSON.stringify(obj);
        msg_socket.send(data);
    } else {
        connect_message_server_use_ajax(obj);
    }
}

// ----------------------------------------------------------------------------
