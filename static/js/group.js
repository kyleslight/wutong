var isLoginBox = false;
var isRegisterBox = false;
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

    $(window).scroll(function(){
        // scrollLoading(".communication");
    });

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
    var waittingFlag=false;
    $(".groupOptions a").click(function() {
        if (!waittingFlag) {
            waittingFlag=true;
            setTimeout(function(){
                waittingFlag=false;
            },2000);
        }else{
            return false;
        }
        var indexOfDetailItem = $(".groupOptions a").index($(this));
        var groupOptionShowBox=$(".groupOptionShow").eq(indexOfDetailItem);
        if ($(".active").length==0) {
            groupOptionShowBox.addClass("prepare").css("left", "960px").show(function() {
                $(".groupItem").slideDown(500, function() {
                    groupOptionShowBox.removeClass("prepare").addClass("active").animate({
                        left: 0
                    }, 500);
                });
            });
        }else{
            var activeIndexOfDetailItem=$(".groupOptionShow").index($(".active"));
            if (activeIndexOfDetailItem==indexOfDetailItem) {
                return false;
            };
            $(".active").animate({
                left:-960
            },500,function(){
                $(".groupItem").css({height:$(".active").innerHeight()});
                $(".active").hide().removeClass("active");
                $(".groupItem").animate({
                    height:groupOptionShowBox.innerHeight()
                },500,function(){
                    groupOptionShowBox.addClass("prepare").css("left", "960px").show(function(){
                        groupOptionShowBox.animate({
                            left: 0
                        }, 500, function() {
                            groupOptionShowBox.removeClass("prepare").addClass("active");
                            $(".groupItem").css("height", "auto");
                        });
                    });
                });
            });
        };
        return false;
    })
    // group item back
    $(".optionBack").click(function() {
        var indexOfOptionBack = $(".optionBack").index($(this));
        var groupOptionBack=$(".groupOptionShow").eq(indexOfOptionBack);
        groupOptionBack.animate({
            left: -960
        },500,function() {
            $(".groupItem").slideUp(1000, function() {
                groupOptionBack.hide().removeClass("active");;
            });
            $(".bulletinCon").fadeOut(500);
        });
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
        $(".selectedMember").removeClass("selectedMember");
        $(this).addClass("selectedMember");
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
    });

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

    $("#collectTopic").click(function(){
        var url = '/u/collection';
        var topic_id = location.pathname.match('/t/(\\d+)')[1];
        $.post(url, {
            'type': '2',
            'id': topic_id
        }, function(data){
            var err = getError(data);
            if (err) {
                console.log(err);
                return;
            }
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

    // 当整个页面加载完毕时加载
    $(window).load(function() {
        connect_message_server();

        var history_url = location.pathname + '/session/history';
        var prefix;
        // is group page ?
        if (location.pathname.search('/g/\\d+') == 0)
            prefix = location.pathname;
        else
            prefix = $(".topicLocation a")[0].href;

        $.getJSON(history_url, function(data) {
            var err = getError(data);
            if (err) {
                console.log(err);
                return;
            }
            for (var i = 0; i < data.length; i++) {
                data[i] = JSON.parse(data[i]);
                if (data[i].title)
                    renderTemplateAppend("#topic-template", data[i], "#communication");
                else
                    renderTemplateAppend("#chat-template", data[i], "#communication");
            }
        });

        // 加载成员信息
        $.getJSON(prefix + '/member', function(data) {
            var err = getError(data);
            if (err) {
                console.log(err);
                return;
            }
            for (var i = 0; i < data.length; i++) {
                switch(data[i].position_level) {
                case '2':
                    data[i].position = '成员';
                    break;
                case '3':
                    data[i].position = '副组长';
                    break;
                case '4':
                    data[i].position = '组长';
                    break;
                }
                var birthday = data[i].birthday;
                data[i].age = birthday ? getAge(birthday) : null;
                renderTemplateAfter('#member-template', data[i]);
            }
        });

        // 加载作品信息
        $.getJSON(prefix + '/article', function(data) {
            var err = getError(data);
            if (err) {
                console.log(err);
                return;
            }
            for (var i = 0; i < data.length; i++) {
                renderTemplateAfter('#article-template', data[i]);
            }
        });
    });
});

function getAge(strBirthday) {
    var bDay = new Date(strBirthday),
        nDay = new Date(),
        nbDay = new Date(nDay.getFullYear(),bDay.getMonth(),bDay.getDate()),
        age = nDay.getFullYear() - bDay.getFullYear();
    if (bDay.getTime()>nDay.getTime()) {return '日期有错'}
    return nbDay.getTime()<=nDay.getTime()?age:--age;
}

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
    chatCon = $("#chatData").html();
    // return false;
    if (chatCon.replace(/<div>/g,"").replace(/<\/div>/g,"").replace(/<br>/g,"").length > 1000) {
        showError("请保持字数在1000字以内",2000);
        return;
    };
    if (chatCon == "&lt;ex&gt;") {
        $(".normalChatSend").slideUp(500, function() {
            $(".expandChatSend").slideDown(1000);
        });
        $("#chatData").html("");
        return;
    };
    if (chatCon.length == 0 || chatCon.toString().replace(/(\r)*\n/g, "").replace(/\s/g," ").length == 0) {
        showError("请输入内容",2000);
        $("#communicationData").addClass("littleTremble");
        setTimeout(function() {
            $("#communicationData").removeClass("littleTremble");
        }, 1000);
        return;
    };
    var chatConBr=chatCon.match(/<br>/g);
    var chatConEnter=chatCon.match(/<div>/g);
    if (chatConBr) {
        if (chatConBr.length>30) {
            showError("刷屏禁止",2000);
            return;
        };
    };
    if (chatConEnter) {
        if (chatConEnter.length>30) {
            showError("刷屏禁止",2000);
            return;
        };
    };
    // chatCon=chatCon.replace(/</g,"&lt").replace(/>/g,"&gt");
    chatCon=chatCon.httpHtml();
    chatCon=chatCon.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");

    $("#chatData").html("");
    // send message to server, TODO: please refactor
    message = {
        type: "message",
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
        type: "message",
        content: expandChatCon,
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
        type: "topic",
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
    return;
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

function turnToPlainText(e){
    var sel, range;
    e.preventDefault();
    var data=e.clipboardData.getData('Text');
    var chatBox=document.getElementById('chatData');
    sel = window.getSelection();
    var range=window.getSelection().getRangeAt(0);
    range.deleteContents();
    var el = document.createElement('p');
    el.innerHTML = data;
    var frag = document.createDocumentFragment(), node, lastNode;
    while ((node = el.firstChild)) {
        lastNode = frag.appendChild(node);
    }
    range.insertNode(frag);
    if (lastNode) {
        range = range.cloneRange();
        range.setStartAfter(lastNode);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
    }
}

// ----------------------------------------------------------------------------
// 自适应连接
var connect_path = location.pathname + "/session";

function connect_message_server() {
    if (WebSocket) {
        console.log('使用websocket进行数据交换');
        connect_message_server_use_websocket();
    } else {
        console.log('使用ajax进行数据交换');
        connect_message_server_use_ajax();
    }
}

function connect_message_server_use_ajax() {
    var url = connect_path + "/ajax";
    msg_socket = {
        type: 'ajax',
        reconnect_time: 1,
        send: function(jsonstr) {
            $.ajax({
                url: url,
                type: 'POST',
                data: {'message': jsonstr},
                success: function(data) {
                    var err = getError(data);
                    if (err) {
                        if (!checkLogin)
                            showError("请先登录",2000);
                        if (err.msg == '')
                            showError("若想参与该小组讨论请加入该小组",2500);
                    }
                },
                error: function() {
                    console.log('ajax unknow error');
                }
            });
        },
        onmessage: function() {
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data) {
                    var err = getError(data);
                    if (err) {
                        console.log(err);
                        return;
                    }
                    data = JSON.parse(data);
                    if (data.title)
                        renderTemplatePrepend("#topic-template", data, "#communication");
                    else
                        renderTemplatePrepend("#chat-template", data, "#communication");
                    showParaFirst();
                    removeMessage();
                    msg_socket.reconnect_time = 1;
                    msg_socket.onmessage();
                },
                error: function() {
                    msg_socket.connect_state = 'closed';
                    console.log('连接失败, ' + msg_socket.reconnect_time + '秒后重新连接');
                    setTimeout(msg_socket.onmessage, msg_socket.reconnect_time * 1000);
                    if (msg_socket.reconnect_time < 30)
                        msg_socket.reconnect_time *= 2;
                }
            });
        },
    };

    msg_socket.sendJSON = socket_sendJSON;
    msg_socket.onmessage();
}

function connect_message_server_use_websocket() {
    var url = "ws://" + location.host + connect_path + "/websocket";
    WebSocket.reconnect_time = 1;
    msg_socket = new WebSocket(url);
    msg_socket.type = 'websocket';
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

function socket_onmessage(data) {
    var err = getError(data);
    if (err) {
        if (!checkLogin)
            showError("请先登录",2000);
        if (err.msg == '')
            showError("若想参与该小组讨论请加入该小组",2500);
        return false;
    }
    data = JSON.parse(data.data);
    // TODO: maybe don't need
    // data=data.replace(/<script/g,"&lt;script").replace(/<\/script>/g,"&lt;/script&gt;");
    if (data.title)
        renderTemplatePrepend("#topic-template", data, "#communication");
    else
        renderTemplatePrepend("#chat-template", data, "#communication");
    showParaFirst();
    removeMessage();
}

function socket_sendJSON(obj) {
    var data = JSON.stringify(obj);
    if (msg_socket.type == 'websocket' && msg_socket.readyState != msg_socket.OPEN)
        connect_message_server_use_ajax();
    msg_socket.send(data);
}

// ----------------------------------------------------------------------------
