var isLoginBox=false;
var isRegisterBox=false;
var isOtherOptionShow=false;
var activeIndex=-1;
var elapseTime = 4500;
var shortElapseTime=4000;
var _showwel_flag = true;
var _last_post_id;

var url = "ws://" + location.host + location.pathname + "/message";
var msg_socket = new WebSocket(url);
msg_socket.onclose = function() {};

$(document).ready(function(){
    //check sex of the member
    renderMaleAndFemale();
    // $.getJSON("/foo", function (data) {
    //     data.groupName;
    // });

    // navrighton effect
    $("#username").mouseover(function(){
        $(this).css("background","white");
        $(this).children("#usernameHover").css("color","#680");
        $(".userExpand").show();
    });
    $("#username").mouseleave(function(){
        $(this).css("background","transparent");
        $(this).children("#usernameHover").css("color","white");
        $(".userExpand").hide();
    })

    // login and register
    $("#loginSubmitButton").click(function() {
        var loginUsername=$("#loginUsername").val();
        var loginPassword=$("#loginPassword").val();
        $.post("/login", {
            username:loginUsername,
            password:loginPassword
        }, function (response) {
            if (response == "success") {
                // TODO: process user_info
                var username;
                $.getJSON("/account/userinfo", function (data) {
                    console.log(data);
                    username = data.penname;
                });

                $(".navrightoff").fadeOut(function(){
                    $(".navrighton").fadeIn();
                    $("#username").children().val(username);
                    // TODO: you should change this
                    $("#usernameHover").text(username);
                    loginBoxFade();
                });
            } else if (response == "failed") {
                alert("loginfailed");
            }
        });
    });

    $("#registerSubmitButton").click(function() {
        var registerUsername=$("#registerUsername").val();
        var registerEmail=$("#registerEmail").val();
        var registerPassword=$("#registerPassword").val();
        var registerRepassword=$("#registerRepassword").val();
        if (registerPassword!=registerRepassword) {
            alert("password and repassword must be the same vaule");
            return;
        };
        alert(registerEmail);
        $.post("/register",{
            username:registerUsername,
            password:registerPassword,
            email:registerEmail
        },function(){
            registerBoxFade();
        });
    });
    // logout
    $("#logout").click(function(){
        // logout function
        $.post("/logout");
        $(".navrighton").fadeOut(function(){
            $(".navrightoff").fadeIn();
        });
        // $("#username").children().val(username);
    })

    // loginBox and registerBox
    $("#login").click(function(){
        if (_showwel_flag == true){
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, elapseTime);
            if (isRegisterBox||isLoginBox) {
                return;
            }else{
                loginBoxShow();
            }
        }
        return false;
    });
    $("#loginBack").click(function(){
        loginBoxFade();
        isLoadBox=false;
        return false;
    });
    $("#register").click(function(){
        if (_showwel_flag == true){
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, elapseTime);
            if (isRegisterBox||isLoginBox) {
                return;
            }else{
                registerBoxShow();
            }
        }
        return false;
    });
    $("#registerBack").click(function(){
        registerBoxFade();
        isRegisterBox=false;
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
            if (isOtherOptionShow) {
                $("#groupOptionShow"+activeIndex).removeClass("active").addClass("outOfView");
                $("#groupOptionShow"+activeIndex).animate({left:"-960px"},1500,function(){
                    $(this).slideUp(400);
                    $("#groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").show(function(){
                        var prepareHeight=$(this).height()+32+"px";
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
                $("#changeSendState").html("切换为聊天模式");
            });
        }else{
            $(".topicSend").slideUp(1000,function(){
                $(".chatSend").slideDown(500);
                $("#changeSendState").html("切换为话题模式");
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

    msg_socket.onmessage = function(e) {
        var data = e.data;
        if (!data)
            return;

        topic_id = $("#communication li:first-child").attr("id");
        topic_id = topic_id ? topic_id.replace("topic_", "") : '0';
        _last_post_id = topic_id;

        var entry = JSON.parse(data);
        if (parseInt(entry.id, 10) <= parseInt(_last_post_id, 10))
            return;
        else
            _last_post_id = entry.id;

        entry.submit_time=entry.submit_time.toString().substring(5,19);
        condata = $(condata);
        var condata="<li id='topic_"+entry.id+"'>"+"<a href='#'><img src='"+entry.avatar+"'/></a><div class='talkmain'><div class='username'><a href='#'>"+entry.penname+"</a></div><div class='talkcontent'>"+entry.content+"</div></div><div class='timeshow'>"+entry.submit_time+"</div></li>";
        $("#communication").prepend(condata);

        var thedata=$("#communication").children().size();
        if (thedata>30) {
            for (var i = 30; i < thedata; i++) {
                $("#communication").children("li").eq(i).remove();
            }
        }
    }
});

// function for login and register
function loginBoxShow(){
    $("#loginBox").show().css("opacity","0");
    var heightOfLRBox=$("#loginBox").height()+"px";
    $("#lrBoxWrap").animate({height:heightOfLRBox},1000,function(){
        $("#loginBox").animate({opacity:1.0},1000,function(){
            isLoginBox=true;
            isRegisterBox=false;
        });
    });
}


function loginBoxFade(){
    $("#loginBox").animate({opacity:0.0},1000,function(){
        $("#lrBoxWrap").animate({height:"0"},1000,function(){
            $("#loginBox").hide();
            isLoginBox=false;
            isRegisterBox=false;
        });
    })
}

function registerBoxShow(){
    $("#registerBox").show().css("opacity","0");
    var heightOfLRBox=$("#registerBox").height()+"px";
    $("#lrBoxWrap").animate({height:heightOfLRBox},1000,function(){
        $("#registerBox").animate({opacity:1.0},1000,function(){
            isLoginBox=false;
            isRegisterBox=true;
        });
    });
}

function registerBoxFade(){
    $("#registerBox").animate({opacity:0.0},1000,function(){
        $("#lrBoxWrap").animate({height:"0"},1000,function(){
            $("#registerBox").hide();
            isLoginBox=false;
            isRegisterBox=false;
        });
    })
}


// function for submit data
function submitChatData(){
    if($("#chatData").val().length>1000){
        alert("请保持字数在1000字以内");
        return;
    }
    chatCon=$("#chatData").val().httpHtml();
    chatCon=chatCon.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");
    if(chatCon.length==0){
        alert("Please input content");
        return;
    }
    var thedata=$(".communication").children().size();
    if (thedata>30) {
        for (var i =30; i < thedata; i++) {
            $("#communication").children("li").eq(i).remove();
        }
    }

    data = {};
    data["content"] = chatCon;
    data["title"] = null;
    data = JSON.stringify(data);
    msg_socket.send(data);
    $("#chatData").val("");
}

function submitTopicData(){
    var topicCon=$("#topicData").val();
    if (topicCon.length==0) {
        alert("Please input content");
        return;
    };
    $.ajax({
        type:"POST",
        dataType:"json",
        url:"/test",
        timeout:80000,
        data:{
            option: "send_topic",
            content:topicCon
        },
        success:function(data,textStatus){
            // $("body.view").html()="";
        }
    });
    $(window.frames["ueditor_0"].document).find("body.view").html("");
    return false;
}
/*
function foo() {
    $.post("/test", {
        option: "send_normal",
        data: data
    });
}
*/
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

String.prototype.httpHtml = function(){
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}
