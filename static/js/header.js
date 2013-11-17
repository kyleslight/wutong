var isLoginBox=false;
var isRegisterBox=false;
var isOtherOptionShow=false;
var activeIndex=-1;
var elapseTime = 4500;
var shortElapseTime=4000;
var _showwel_flag = true;
var _last_post_id;
// var userInfo=[{"userName":"","userId":0}];
var isLoginPasswordFocus=false;
var isRegisterRepasswordFocus=false;

// get unsync information
unsycUser();

$(document).ready(function(){
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
    $("#message").mouseover(function(){
        $("#msgNum").css({"background":"pink","color":"darkred","box-shadow":"#FFF"});
        // $("#msgNum").addClass("tremble");
    });
    $("#message").mouseleave(function(){
        $("#msgNum").css({"background":"pink","color":"#680","box-shadow":"#AAA"});
        // $("#msgNum").removeClass("tremble");
    })

    testTremble();


    // login and register
    $("#loginSubmitButton").click(function() {
        loginSubmit();
    });
    // quick login
    $("#loginPassword").focus(function(){
        isLoginPasswordFocus=true;
        $(window).keyup(function(e){
            var keyCode=e.keyCode;
            if (keyCode==13&&isLoginPasswordFocus) {
                loginSubmit();
            }
            return false;
        });
    })
    $("#loginPassword").blur(function(){
        isLoginPasswordFocus=false;
    })

    $("#registerSubmitButton").click(function() {
        registerSubmit();
    });
    // quick register
    $("#registerRepassword").focus(function(){
        isRegisterRepasswordFocus=true;
        $(window).keyup(function(e){
            var keyCode=e.keyCode;
            if (keyCode==13&&isRegisterRepasswordFocus) {
                registerSubmit();
            }
            return false;
        });
    })
    $("#registerRepassword").blur(function(){
        isRegisterRepasswordFocus=false;
    })
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
                var loginUsernamePosition = 0;
                var loginUsernameFocus = document.getElementById("loginUsername");
                loginUsernameFocus.setSelectionRange(loginUsernamePosition, loginUsernamePosition);
                loginUsernameFocus.focus();
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
                var registerUsernamePosition = 0;
                var registerUsernameFocus = document.getElementById("registerUsername");
                registerUsernameFocus.setSelectionRange(registerUsernamePosition, registerUsernamePosition);
                registerUsernameFocus.focus();
            }
        }
        return false;
    });
    $("#registerBack").click(function(){
        registerBoxFade();
        isRegisterBox=false;
        return false;
    });

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

function loginSubmit(){
    var loginUsername=$("#loginUsername").val();
        var loginPassword=$("#loginPassword").val();
        $.post("/login", {
            username:loginUsername,
            password:loginPassword
        }, function (response) {
            if (response == "success") {
                // TODO: process user_info
                var username;
                $.getJSON("/u/info", function (data) {
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
                unsycUser();
                unsyncGroup();
            } else if (response == "failed") {
            	$("#loginBox").addClass("littleTremble");
            	setTimeout(function(){
            		$("#loginBox").removeClass("littleTremble");
            	},1000);
            }
        });
}


function registerSubmit(){
    var registerUsername=$("#registerUsername").val();
        var registerEmail=$("#registerEmail").val();
        var registerPassword=$("#registerPassword").val();
        var registerRepassword=$("#registerRepassword").val();
        if (registerPassword!=registerRepassword) {
            alert("password and repassword must be the same vaule");
            $("#loginBox").addClass("littleTremble");
            	setTimeout(function(){
            	$("#loginBox").removeClass("littleTremble");
            },1000);
            return;
        };
        $.post("/register",{
            username:registerUsername,
            password:registerPassword,
            email:registerEmail
        },function(){
            registerBoxFade();
        });
}

function testTremble(){
	document.getElementById("msgNum").innerHTML=parseInt($("#msgNum").text())+1;
	$("#msgNum").addClass("tremble");
	setTimeout(function(){$("#msgNum").removeClass("tremble");},2000)
	setTimeout(function(){testTremble()},10000);
}

function unsycUser(){
    // get user infomation
    $.ajax({
        url:"/u/info",
        type:"GET",
        dataType:"json",
        async:false,
        success:function(data){
            userInfo[0].userName = data.penname;
            userInfo[0].userId = data.uid;
            $(".navrightoff").fadeOut(10,function(){
                $(".navrighton").fadeIn(10);
                $("#usernameHover").text(userInfo[0].userName);
            });
        }
    })
}

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

