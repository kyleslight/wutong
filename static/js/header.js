var isLoginBox = false;
var isRegisterBox = false;
var isOtherOptionShow = false;
var activeIndex = -1;
var elapseTime = 4500;
var shortElapseTime = 4000;
var _showwel_flag = true;
var _last_post_id;
var userInfo;
var groupInfo;
var isLoginPasswordFocus = false;
var isRegisterRepasswordFocus = false;
var ueditor=null;
var insertImageState=-1;
var activeNoteID=-1;
var illegalCharacter=/[`~!@#$%^&*()_+<>?:"{},.\/;'[\]]/im;
var lessIllegalCharacter=/[`~@#$%^&*()_+<>:"{},.\'[\]]/im;
var checkLogin=false;

// get unsync information
unsycUser();

$(document).ready(function() {
    checkIsLogin();

    $(".preload").removeClass("preload");
    // get user info
    $.getJSON("/u/info", function (data) {
        var username;
        username = data.penname;
        $(".navrightoff").fadeOut(10,function(){
            $(".navrighton").fadeIn(10);
            $("#username").children().val(username);
            $("#usernameHover").text(username);
        });
        if (location.pathname.slice(0,9)=="/a/create") {
            $(".write").show();
        };
    });
    // return to top icon show
    $(window).scroll(function() {
        var top = $(window).scrollTop();
        if (top > 200) {
            var realHeight = (top + (window.screen.availHeight) / 2) + 'px';
            $('#return_top').removeClass('none');
            $('#return_top').stop();
            $('#return_top').animate({
                top: realHeight
            }, 500);
        } else {
            $('#return_top').addClass('none');
        }
        return false;
    })
    // return to top
    $("#return_top").click(function() {
        $('html,body').animate({
            scrollTop: 0
        }, 1000);
        return false;
    });
    // navrighton effect
    $("#username").mouseover(function() {
        $(this).css("background", "white");
        $(this).children("#usernameHover").css("color", "#680");
        $(".userExpand").show();
        $("#usernameHover").css({"color":"#680"});
    });
    $("#username").mouseleave(function() {
        $(this).css("background", "transparent");
        $(this).children("#usernameHover").css("color", "white");
        $(".userExpand").hide();
        $("#usernameHover").css({"color":"white"});
    })
    $("#message").mouseover(function() {
        $("#msgNum").css({
            "background": "pink",
            "color": "darkred",
            "box-shadow": "#FFF"
        });
        // $("#msgNum").addClass("tremble");
    });
    $("#message").mouseleave(function() {
        $("#msgNum").css({
            "background": "pink",
            "color": "#680",
            "box-shadow": "#AAA"
        });
        // $("#msgNum").removeClass("tremble");
    })

    // testTremble();


    // login and register
    $("#loginSubmitButton").click(function() {
        loginSubmit();
    });
    // quick login
    $("#loginPassword").focus(function() {
        isLoginPasswordFocus = true;
        $(window).keyup(function(e) {
            var keyCode = e.keyCode;
            if (keyCode == 13 && isLoginPasswordFocus) {
                loginSubmit();
            }
            return false;
        });
    });
    $("#loginPassword").blur(function() {
        isLoginPasswordFocus = false;
    });
    $("#turnToRegisterBox,#turnToLoginBox").click(function(){
        if ($(this).attr("id")=="turnToRegisterBox") {
            $("#loginBox").hide();
            $("#registerBox").show();
            $("#lrBoxWrap").height($("#registerBox").height());
        }else{
            $("#loginBox").show();
            $("#registerBox").hide();
            $("#lrBoxWrap").height($("#loginBox").height());
        }
        return false;
    });

    $("#registerSubmitButton").click(function() {
        registerSubmit();
    });
    // quick register
    $("#registerRepassword").focus(function() {
        isRegisterRepasswordFocus = true;
        $(window).keyup(function(e) {
            var keyCode = e.keyCode;
            if (keyCode == 13 && isRegisterRepasswordFocus) {
                registerSubmit();
            }
            return false;
        });
    });
    $("#registerRepassword").blur(function() {
        isRegisterRepasswordFocus = false;
    })
    // logout
    $("#logout").click(function() {
        // logout function
        $.post("/logout");
        $(".navrighton").fadeOut(function() {
            $(".navrightoff").fadeIn();
            if (location.pathname.slice(0,9)=="/a/create") {
                showError("创作作品前请先登录",2000);
            };
        });
        logOutEffect();
        checkIsLogin();
    });

    // loginBox and registerBox
    $("#login").click(function() {
        if (_showwel_flag == true) {
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, elapseTime);
            if (isRegisterBox || isLoginBox) {
                return;
            } else {
                loginBoxShow();
                var loginUsernamePosition = 0;
                var loginUsernameFocus = document.getElementById("loginUsername");
                loginUsernameFocus.setSelectionRange(loginUsernamePosition, loginUsernamePosition);
                loginUsernameFocus.focus();
            }
        }
        return false;
    });
    $("#loginBack").click(function() {
        loginBoxFade();
        isLoadBox = false;
        return false;
    });
    $("#register").click(function() {
        if (_showwel_flag == true) {
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, elapseTime);
            if (isRegisterBox || isLoginBox) {
                return;
            } else {
                registerBoxShow();
                var registerUsernamePosition = 0;
                var registerUsernameFocus = document.getElementById("registerUsername");
                registerUsernameFocus.setSelectionRange(registerUsernamePosition, registerUsernamePosition);
                registerUsernameFocus.focus();
            }
        }
        return false;
    });
    $("#registerBack").click(function() {
        registerBoxFade();
        isRegisterBox = false;
        return false;
    });
    // my collection
    var numOfCollectionList = 1;
    var heightOfMycollection = 123 + numOfCollectionList * 55;
    $("#myCollection").click(function() {
        $(".myCollectionWarp").animate({
            height: heightOfMycollection
        }, function() {
            $(".myCollection").fadeIn(500);
        });
    });
    $("#myCollectionBack").click(function() {
        $(".myCollection").fadeOut(500, function() {
            $(".myCollectionWarp").animate({
                height: 0
            });
        });
    })
    // my note
    $("#myNote").click(function() {
        $(".myNoteWrap").animate({
            height: 415
        }, function() {
            $(".myNote").fadeIn(500);
            // update note
            $.getJSON("/u/memo",function(data){
                $(".myNoteListWrap").empty();
                if (data.length==undefined) {
                    $("#deleteCurrentNote,#saveCurrentNote").hide();
                    $("#createNewNote").show();
                    return false;
                }else{
                    var noteNum=data.length-1;
                    activeNoteID=data[noteNum].id;
                    $(".myCurrentNoteTitle").val(data[noteNum].title);
                    $(".myCurrentNoteContent").val(data[noteNum].content);
                    $(".myCurrentNoteTime").text(data[noteNum].create_time.slice(0,10));
                    for (var i = 0; i < data.length; i++) {
                        var preNoteList='<a href="#" id="'+data[i].id+'" class="myNoteList" onclick="selectNote('+data[i].id+')">'+data[i].title+'</a>';
                        $(".myNoteListWrap").prepend(preNoteList);
                    };
                    $("#"+activeNoteID).addClass("activeMyNoteList");
                }
            });
        });
    });
    $("#myNoteBack").click(function() {
        $(".myNote").fadeOut(500, function() {
            $(".myNoteWrap").animate({
                height: 0
            });
        });
    });
    $("#addNote").click(function(){
        $(".myCurrentNoteTitle").val("");
        $(".myCurrentNoteContent").val("");
        $(".myCurrentNoteTime").text("");
        $("#deleteCurrentNote,#saveCurrentNote").hide();
        $("#createNewNote").show();
        $(".myNoteList").removeClass("activeMyNoteList");
        $("#addNote").addClass("activeMyNoteList").text("创建中...");
    });
    // create note
    $("#createNewNote").click(function(){
        if ($(".myCurrentNoteTitle").val()=="") {
            showError("请填写标题",2000);
            return false;
        };
        $.post("/u/memo",{
            "title":$(".myCurrentNoteTitle").val(),
            "content":$(".myCurrentNoteContent").val()
        },function(data){
            var newNote=eval ("(" + data + ")");
            var newNoteTitle='<a href="#" id="'+newNote.id+'" class="myNoteList" onclick="selectNote('+newNote.id+')">'+newNote.title+'</a>';
            activeNoteID=newNote.id;
            $(".myNoteListWrap").prepend(newNoteTitle);
            $(".myCurrentNoteTitle").val(newNote.title);
            $(".myCurrentNoteContent").val(newNote.content);
            $(".myCurrentNoteTime").text(newNote.create_time.slice(0,10));
            $("#deleteCurrentNote,#saveCurrentNote").show();
            $("#createNewNote").hide();
            $(".myNoteList").removeClass("activeMyNoteList");
            $("#"+activeNoteID).addClass("activeMyNoteList");
            $("#addNote").text("创建便笺");
            showError("便笺 "+newNote.title+" 创建成功",2000);
        });
    });
    // update note
    $("#saveCurrentNote").click(function(){
        if (activeNoteID==-1) {
            return false;
        };
        if ($(".myCurrentNoteTitle").val()=="") {
            showError("请填写标题",1500);
            return false;
        };
        $.post("/u/memo/update",{
            "memo_id":activeNoteID,
            "title":$(".myCurrentNoteTitle").val(),
            "content":$(".myCurrentNoteContent").val()
        },function(){
            showError("成功保存便笺",1000);
            $("#"+activeNoteID).text($(".myCurrentNoteTitle").val());
        });
    });
    // delete note
    $("#deleteCurrentNote").click(function(){
        if (activeNoteID==-1) {
            return false;
        };
        $.post("/u/memo/delete",{
            "memo_id":activeNoteID,
        },function(){
            showError("成功删除便笺",1000);
            // // TODO: refresh notes
            // $("#"+activeNoteID).text($(".myCurrentNoteTitle").val());
            $.getJSON("/u/memo",function(data){
                $(".myNoteListWrap").empty();
                if (data.length==undefined) {
                    $("#deleteCurrentNote,#saveCurrentNote").hide();
                    $("#createNewNote").show();
                    return false;
                }else{
                    var noteNum=data.length-1;
                    activeNoteID=data[noteNum].id;
                    $(".myCurrentNoteTitle").val(data[noteNum].title);
                    $(".myCurrentNoteContent").val(data[noteNum].content);
                    $(".myCurrentNoteTime").text(data[noteNum].create_time.slice(0,10));
                    for (var i = 0; i < data.length; i++) {
                        var preNoteList='<a href="#" id="'+data[i].id+'" class="myNoteList" onclick="selectNote('+data[i].id+')">'+data[i].title+'</a>';
                        $(".myNoteListWrap").prepend(preNoteList);
                    };
                    $("#"+activeNoteID).addClass("activeMyNoteList");
                }
            });
        });
    });

    var numOfMessageList = 0;
    var heightOfMyMessage = 0;
    // my message
    $("#message").click(function() {
        numOfMessageList = $(".activeMessagePart").children("li").size() + 1;
        heightOfMyMessage = 56 + numOfMessageList * 60;
        $(".myMessageWarp").animate({
            height: heightOfMyMessage
        }, function() {
            $(".myMessage").fadeIn(500);
        });
        var activeIndexOfMessagePart = $(".myMessagePartContent").index($(".activeMessagePart"));
        $(".myMessagePartButton").eq(activeIndexOfMessagePart).css("color", "#680");
    })
    $("#myMessageBack").click(function() {
        $(".myMessage").fadeOut(500, function() {
            $(".myMessageWarp").animate({
                height: 0
            });
        });
    })
    $(".myMessagePartButton").click(function() {
        $(".myMessagePartButton").css("color", "#444");
        $(this).css("color", "#680");
        var indexOfMessagePartButton = $(".myMessagePartButton").index($(this));
        var activeIndexOfMessagePart = $(".myMessagePartContent").index($(".activeMessagePart"));
        $(".myMessagePartContent").eq(activeIndexOfMessagePart).removeClass("activeMessagePart").slideUp(500, function() {});
        $(".myMessagePartContent").eq(indexOfMessagePartButton).slideDown(500).addClass("activeMessagePart");
        numOfMessageList = $(".activeMessagePart").children("li").size() + 1;
        heightOfMyMessage = 56 + numOfMessageList * 60;
        $(".myMessageWarp").animate({
            height: heightOfMyMessage
        });
    });

    // image upload back
    $("#uploadImageBack").click(function(){
        $("section#main,#uploadImageBack,#info_zone,.mask").hide();
        return false;
    })
});

// function for login and register
function checkIsLogin(){
    $.ajax({
        url: "/u/info",
        type: "GET",
        dataType: "json",
        async: false,
        success: function(data) {
            checkLogin=true;
            return;
        },
        error:function(){
            checkLogin=false;
            return;
        }
    });
}

function loginBoxShow() {
    $("#loginBox").show().css("opacity", "0");
    var heightOfLRBox = $("#loginBox").height() + "px";
    $("#lrBoxWrap").animate({
        height: heightOfLRBox
    }, 300, function() {
        $("#loginBox").animate({
            opacity: 1.0
        }, 300, function() {
            isLoginBox = true;
            isRegisterBox = false;
        });
    });
}


function loginBoxFade() {
    $("#loginBox").animate({
        opacity: 0.0
    }, 300, function() {
        $("#lrBoxWrap").animate({
            height: "0"
        }, 300, function() {
            $("#loginBox").hide();
            isLoginBox = false;
            isRegisterBox = false;
        });
    })
}

function registerBoxShow() {
    $("#registerBox").show().css("opacity", "0");
    var heightOfLRBox = $("#registerBox").height() + "px";
    $("#lrBoxWrap").animate({
        height: heightOfLRBox
    }, 300, function() {
        $("#registerBox").animate({
            opacity: 1.0
        }, 300, function() {
            isLoginBox = false;
            isRegisterBox = true;
        });
    });
}

function registerBoxFade() {
    $("#registerBox").animate({
        opacity: 0.0
    }, 300, function() {
        $("#lrBoxWrap").animate({
            height: "0"
        }, 300, function() {
            $("#registerBox").hide();
            isLoginBox = false;
            isRegisterBox = false;
        });
    })
}

function loginSubmit() {
    var loginUsername = $("#loginUsername").val();
    var loginPassword = $("#loginPassword").val();
    loginAction(loginUsername,loginPassword);
}

function loginAction(loginUsername,loginPassword){
    $.post("/login", {
        username: loginUsername,
        password: loginPassword
    }, function(data) {
        if (data == "failed") {
            showError("登录失败",2000);
        }else{
            var username;
            $.getJSON("/u/info", function(data) {
                console.log(data);
                username = data.penname;
                $(".navrightoff").fadeOut(function() {
                    $(".navrighton").fadeIn();
                    $("#username").children().val(username);
                    $("#usernameHover").text(username);
                    loginBoxFade();
                });
            });
            unsycUser();
            if(location.pathname.slice(0,2)=="/t"||location.pathname.slice(0,2)=="/g"){
                checkGroupPremission();
            };
            if (location.pathname.slice(0,9)=="/a/create") {
                $(".write").show();
            };
        }
    });
    checkIsLogin();
}

function registerSubmit() {
    var registerUsername = $("#registerUsername").val(),
        registerEmail = $("#registerEmail").val(),
        registerPassword = $("#registerPassword").val(),
        registerRepassword = $("#registerRepassword").val();

    // check username
    if (registerUsername=="") {
        showError("用户名不能为空",2000);
        return false;
    };
    if (illegalCharacter.test(registerUsername)) {
        showError("用户名包含非法字符",2000);
        return false;
    };
    if (registerUsername.length>20) {
        showError("用户名请限定在20字以内",2000);
        return false;
    };
    $.get("/account/check?is_account_exists&v="+registerUsername+"",function(data){
        if (data=="true") {
            showError("用户名 "+registerUsername+" 已存在",2000);
            return false;
        };
    });

    // check email
    if (!checkEmail(registerEmail)) {
        showError("Email地址不合法",2000);
        return false;
    };

    // check password
    if (registerPassword != registerRepassword) {
        showError("两次密码不一致",2000);
        return false;
    };
    if (registerPassword=="") {
        showError("密码不能为空",2000);
        return false;
    };
    if (registerPassword.length>30) {
        showError("密码长度不能超过30",2000);
        return false;
    };

    $.post("/register", {
        username: registerUsername,
        password: registerPassword,
        email: registerEmail
    }, function() {
        showError("欢迎加入梧桐,"+registerUsername+"!<br>目前是测试期间，不需要邮箱激活~",5000);
        loginAction(registerUsername,registerPassword);
        registerBoxFade();
    });
}

function testTremble() {
    document.getElementById("msgNum").innerHTML = parseInt($("#msgNum").text()) + 1;
    $("#msgNum").addClass("tremble");
    setTimeout(function() {
        $("#msgNum").removeClass("tremble");
    }, 2000)
    setTimeout(function() {
        testTremble()
    }, 10000);
}

function unsycUser() {
    $.ajax({
        url: "/u/info",
        type: "GET",
        dataType: "json",
        async: false,
        success: function(data) {
            userInfo = data
            $(".navrightoff").fadeOut(10, function() {
                $(".navrighton").fadeIn(10);
                $("#usernameHover").text(userInfo.penname);
            });
        }
    });
}

function selectNote(noteID){
    $.getJSON("/u/memo/update",{
        "memo_id":noteID
    },function(data){
        $(".myCurrentNoteTitle").val(data.title);
        $(".myCurrentNoteContent").val(data.content);
        $(".myCurrentNoteTime").text(data.create_time.slice(0,10));
        activeNoteID=noteID;
    });
    $("#deleteCurrentNote,#saveCurrentNote").show();
    $("#createNewNote").hide();
    $(".myNoteList").removeClass("activeMyNoteList");
    $("#"+noteID).addClass("activeMyNoteList");
    $("#addNote").text("创建便笺");
}

// insertImageState
// 0:in textarea
// 1:in create
// 2:in buttom comment
// 3:in group chat
// 4:in group topic
// 5:for more...

function insertImage(state){
    $("section#main,#info_zone,#uploadImageBack,#first_load,.mask").show();
    hide(upload_popup);
    url_list.value = '';
    file_list.value = '';
    insertImageState=state;
}

function initUeditor(UEstate){
    var insertImageButtom='<a href="javascript:void(0)" id="insertIamge" title="插入图片" onclick="insertImage('+UEstate+')"></a>'
    $(".edui-for-link").after(insertImageButtom);
};

function activeItemChange(activeItem,activeClassName){
    $("."+activeClassName).removeClass(activeClassName);
    activeItem.addClass(activeClassName);
}

function logOutEffect(){
    $(".myCollection").fadeOut(500, function() {
        $(".myCollectionWarp").animate({
            height: 0
        });
    });

    $(".myNote").fadeOut(500, function() {
        $(".myNoteWrap").animate({
            height: 0
        });
    });

    $(".myMessage").fadeOut(500, function() {
        $(".myMessageWarp").animate({
            height: 0
        });
    });
}

function checkEmail(e){ var i=e.length;     
    var temp = e.indexOf('@');     
    var tempd = e.indexOf('.');     
    if (temp > 1) {     
        if ((i-temp) > 3){     
            if ((i-tempd)>0){     
                return true;     
            }     
        }     
    }     
    return false;     
}     

String.prototype.httpHtml = function() {
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-|:)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}

function showError(errorStatement,duration){
    $(".errorPromptBox").html(errorStatement);
    $(".errorPromptBox").fadeIn();
    setTimeout(function(){
        $(".errorPromptBox").fadeOut();
    },duration);
}