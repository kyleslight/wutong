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
var illegalCharacter=/[`~!@#$%^&*()_+<>?:"{},.\/;'[\]]\s/im;
var lessIllegalCharacter=/[`~@#$%^&*()_+<>:"{},.\'[\]]/im;
var checkLogin=false;
var user;

// get unsync information
unsycUser();

highlightThisPage();

$(document).ready(function() {
    checkIsLogin();

    if (location.pathname == "/a/create") {

    } else if (location.pathname == '/a/browse') {

    } else if (location.pathname == '/g/browse') {

    };
    $(".preload").removeClass("preload");
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

    // search
    $("#searchSubmitButton").click(function(){
        searchStart();
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
    });
    $("#setting").click(function(){
        $(".mySettingWrap").animate({
            height:374
        },function(){
            $(".mySetting").fadeIn(500);
        });
        return false;
    });
    $("#mySettingBack").click(function(){
        $(".mySetting").fadeOut(500,function(){
            $(".mySettingWrap").animate({
                height:0
            });
        });
    });

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
        window.location = location.pathname;
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
        var url = '/u/collection';
        $.getJSON(url, function(data) {
            $(".myCollectionList").remove();
            renderTemplateAfter('#collection-template', data);
        });
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
                var err = getError();
                if (err) {
                    // TODO
                    return;
                }
                $(".myNoteListWrap").empty();
                if (data.length == undefined) {
                    $("#deleteCurrentNote,#saveCurrentNote").hide();
                    $("#createNewNote").show();
                    return false;
                } else {
                    data.forEach(function(item) {
                        renderTemplatePrepend('#memo-template', item, '.myNoteListWrap');
                    });
                    var noteNum=data.length-1;
                    activeNoteID=data[noteNum].id;
                    $(".myCurrentNoteTitle").val(data[noteNum].title);
                    $(".myCurrentNoteContent").val(data[noteNum].content);
                    // TODO: show pretty time
                    $(".myCurrentNoteTime").text(data[noteNum].create_time.slice(0,10));
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
        document.getElementsByClassName("myCurrentNoteTitle")[0].focus();
    });
    // create note
    $("#createNewNote").click(function(){
        var title = $(".myCurrentNoteTitle").val();
        var content = $(".myCurrentNoteContent").val();
        $.post("/u/memo?create",{
            "title": title,
            "content": content
        }, function(data){
            var err = getError(data);
            if (err) {
                // TODO
                return;
            }
            var newNote = data;
            renderTemplatePrepend('#memo-template', newNote, '.myNoteListWrap');
            $(".myCurrentNoteTitle").val(newNote.title);
            $(".myCurrentNoteContent").val(newNote.content);
            $(".myCurrentNoteTime").text(newNote.create_time.slice(0,10));
            $("#deleteCurrentNote,#saveCurrentNote").show();
            $("#createNewNote").hide();
            $(".myNoteList").removeClass("activeMyNoteList");
            $("#"+activeNoteID).addClass("activeMyNoteList");
            $("#addNote").text("创建便笺");
        });
    });
    // update note
    $("#saveCurrentNote").click(function(){
        if (activeNoteID==-1) {
            return false;
        };
        $.post("/u/memo?update",{
            "id":activeNoteID,
            "title":$(".myCurrentNoteTitle").val(),
            "content":$(".myCurrentNoteContent").val()
        },function(){
            var err = getError(data);
            if (err) {
                // TODO
                return;
            }
            showError("成功保存便笺");
            $("#"+activeNoteID).text($(".myCurrentNoteTitle").val());
        });
    });
    // delete note
    $("#deleteCurrentNote").click(function(){
        if (activeNoteID==-1) {
            return false;
        };
        $.post("/u/memo?delete",{
            "id":activeNoteID,
        },function(data){
            var err = getError(data);
            if (err) {
                // TODO
                return;
            }
            $("#No_memo_" + activeNoteID).remove();
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

    $("#loginUsername").blur(function () {
        var account = $("#loginUsername").val();
        if (checkEmail(account, seterr=false)) {
            checkEmailExist(account, function(b) {
                if (!b)
                    perror("邮箱不存在");
            });
        } else {
            checkUsernameExist(account, function(b) {
                if (!b)
                    perror("用户名不存在");
            });
        }
        invokeBlur(this);
    });

    $("#registerUsername").blur(function () {
        var username = $("#registerUsername").val();
        if (checkUsername(username)) {
            checkUsernameExist(username, function(b) {
                if (b)
                    perror("用户名 "+username+" 已存在");
            });
        }
        invokeBlur(this);
    });

    $("#registerEmail").blur(function () {
        var email = $("#registerEmail").val();
        if (checkEmail(email)) {
            checkEmailExist(email, function(b) {
                if (b) {
                    perror("邮箱 " + email + " 已存在");
                }
            });
        }
        invokeBlur(this);
    });

    $("#registerPassword").blur(function () {
        var password = $("#registerPassword").val();
        checkPassword(password);
        invokeBlur(this);
    });

    $("#loginUsername").focus(function () {
        invokeFocus(this);
    });
    $("#loginPassword").focus(function () {
        invokeFocus(this);
    });
    $("#registerUsername").focus(function () {
        invokeFocus(this);
    });
    $("#registerEmail").focus(function () {
        invokeFocus(this);
    });
    $("#registerPassword").focus(function () {
        invokeFocus(this);
    });
    $("#registerRepassword").focus(function () {
        invokeFocus
    });

    $("#loginUsername").bind('input', lengthLimit(30));
    $("#registerUsername").bind('input', lengthLimit(30));
    $("#registerPassword").bind('input', lengthLimit(30));
    $("#registerRepassword").bind('input', lengthLimit(30));
});

function lengthLimit(length) {
    return function () {
        this.value = this.value.slice(0, length);
    }
}
// get error message from recv
function getError(recv) {
    var obj = {};
    try {
        obj = JSON.parse(recv);
    } catch (e) {
        obj = recv;
    }
    if (!obj || obj.errno === undefined || obj.errno == 0)
        return null;
    else
        return obj.msg;
}

// function for login and register
function checkIsLogin(){
    if (user) {
        checkLogin=true;
    } else {
        checkLogin=false;
    }
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
    loginAction(loginUsername, loginPassword);
}

function loginAction(loginUsername,loginPassword){
    $.post("/login", {
        username: loginUsername,
        password: loginPassword
    }, function(data) {
        var err = getError(data);
        if (err) {
            showError("登录失败",2000);
        } else {
            user = data;
            window.location.reload();
        }
    });
    checkIsLogin();
}

var invoked_focus;
var invoked_blur;
var errmsg;

var _invoked_ids = new Array(3);
function setInvokedId(obj) {
    _invoked_ids.shift();
    var tmp = obj.id;
    _invoked_ids.push(tmp);
}

function setError(msg) {
    errmsg = msg;
}

function perror(msg) {
    if (msg)
        errmsg = msg;
    if (errmsg && invoked_blur && invoked_focus &&
            (_invoked_ids[0] !== _invoked_ids[_invoked_ids.length - 1])) {
        showError(errmsg, 1000);
        errmsg = invoked_blur = invoked_focus = null;
    }
}

function invokeBlur(obj) {
    invoked_blur = true;
    perror();
}

function invokeFocus(obj) {
    invoked_focus = true;
    setInvokedId(obj);
    perror();
}

function checkUsernameExist(username, callback){
    $.getJSON("/account?check_username&v=" + username, function(data) {
        if (data.msg == 1) {
            callback(true);
        } else if (data.msg == 0){
            callback(false);
        }
    });
}

function checkEmailExist(email, callback){
    $.getJSON("/account?check_email&v=" + email, function(data) {
        if (data.msg == 1) {
            callback(true);
        } else if (data.msg == 0){
            callback(false);
        }
    });
}

function checkUsername(username){
    if (illegalCharacter.test(username)) {
        setError("用户名包含非法字符");
    } else if (username.length < 2) {
        setError("用户名长度不能小于2位");
    } else if (username.length > 20) {
        setError("用户名请限定在30字以内");
    } else {
        return true;
    }
    return false;
}

function checkPassword(password){
    if (password.length < 6) {
        setError("密码长度不能小于6位");
    } else if (password.length > 30) {
        setError("密码长度不能超过30");
    } else {
        return true;
    }
    return false;
}

function checkEmail(email, seterr){
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (re.test(email)) {
        return true;
    } else {
        if (seterr !== false && email) {
            setError("Email地址不合法");
        }
    }
    return false;
}

function registerSubmit() {
    var username = $("#registerUsername").val();
    var password = $("#registerPassword").val();
    var email = $("#registerEmail").val();

    if (!(checkUsername(username) && checkEmail(email) && checkPassword(password))) {
        perror();
        return;
    }
    if (username == "") {
        showError("用户名不能为空");
        return;
    }
    if (email == "") {
        showError("Email不能为空");
        return;
    }
    if (password == "") {
        showError("用户名不能为空");
        return;
    }
    $.post("/register", {
        nickname: username,
        password: password,
        email: email
    }, function(data) {
        var err = getError(data);
        if (err) {
            // TODO
        } else {
            showError("欢迎加入梧桐, " + username + "!<br>目前是测试期间，不需要邮箱激活~",5000);
            loginAction(username, password);
            registerBoxFade();
        }
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
            var err = getError(data);
            if (err) {
                // TODO
            } else {
                user = data;
                var replynum = user.msg_count.reply;
                var pushnum = user.msg_count.push;

                $("#replyNum").html(replynum);
                $("#opusPushNum").html(pushnum);
                $("#msgNum").html(replynum + pushnum);
                $(".navrightoff").fadeOut(10,function(){
                    $(".navrighton").fadeIn(10);
                    $("#username").children().val(user.nickname);
                    $("#usernameHover").text(user.nickname);
                    $("#myHomepage").parent().attr("href","/user/"+user.nickname);
                });
                if (location.pathname.slice(0,9)=="/a/create") {
                    $(".write").show();
                };
            }
        }
    });
}

function selectNote(noteID){
    $.getJSON("/u/memo",{
        "id":noteID
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


function highlightThisPage(){
    var pathURL=location.pathname;
    if (pathURL.slice(0,2)=="/a"&&pathURL!="/a/create") {
        $("#browse li").addClass("thisPage");
    }else if(pathURL.slice(0,2)=="/g"||pathURL.slice(0,2)=="/t"){
        $("#group li").addClass("thisPage");
    }else if (pathURL=="/a/create") {
        $("#create li").addClass("thisPage");
    };
    return;
}

String.prototype.httpHtml = function() {
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-|:)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}

function showError(errorStatement, duration){
    if (!errorStatement)
        return;
    duration = duration || 1000;
    $(".errorPromptBox").html(errorStatement);
    $(".errorPromptBox").fadeIn();
    setTimeout(function(){
        $(".errorPromptBox").fadeOut();
    },duration);
}

function showHint(searchKeyWord){
    $(".searchSuggestions").empty();

    // test search searchSuggestion
    if (searchKeyWord=="") {
        $(".searchSuggestions").addClass("noBorderBottom");
        return;
    };
    $(".searchSuggestions").removeClass("noBorderBottom");
    var returnWordsNum=Math.floor(Math.random()*8)+2;
    for(var i=0;i<returnWordsNum;i++){
        var searchSuggestionWord=searchKeyWord+generateMixed(2);
        var app='<a class="searchSuggestionsList" href="/search/'+searchSuggestionWord+'">'+searchSuggestionWord+'</a>';
        console.log(app);
        $(".searchSuggestions").prepend(app);
    };
}

function searchStart(){

}

var chars = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];
function generateMixed(n) {
     var res = "";
     for(var i = 0; i < n ; i ++) {
         var id = Math.ceil(Math.random()*35);
         res += chars[id];
     }
     return res;
}

function renderTemplateString(temp, obj) {
    var template = $(temp).html();
    var innerHTML = Mark.up(template, obj);
    return innerHTML;
}

function renderTemplateAfter(temp, obj, target) {
    var innerHTML = renderTemplateString(temp, obj);
    if (target) {
        $(target).after($(innerHTML));
    } else {
        $(temp).after($(innerHTML));
    }
}

function renderTemplatePrepend(temp, obj, target) {
    var innerHTML = renderTemplateString(temp, obj);
    if (target) {
        $(target).prepend($(innerHTML));
    } else {
        $(temp).prepend($(innerHTML));
    }
}
