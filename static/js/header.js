var isLoginBox=false;
var isRegisterBox=false;
var isOtherOptionShow=false;
var activeIndex=-1;
var elapseTime = 4500;
var shortElapseTime=4000;
var _showwel_flag = true;
var _last_post_id;

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

    // login and register
    $("#loginSubmitButton").click(function() {
        loginSubmit();
    });
    // quick login
    $("#loginPassword").focus(function(){
        $(window).keyup(function(e){
            var keyCode=e.keyCode;
            if (keyCode==13) {
                loginSubmit();
            }
            return false;
        });
    })

    $("#registerSubmitButton").click(function() {
        registerSubmit();
    });
    // quick register
    $("#registerRepassword").focus(function(){
        $(window).keyup(function(e){
            var keyCode=e.keyCode;
            if (keyCode==13) {
                registerSubmit();
            }
            return false;
        });
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
            } else if (response == "failed") {
                alert("loginfailed");
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
}
