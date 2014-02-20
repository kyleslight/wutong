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
var searchInputState=false;
var searchSugNum=-1;
var eveCode=-1;
var user;

// get unsync information
unsycUser();

highlightThisPage();

$(document).ready(function() {
    checkIsLogin();

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
    });
    // return to top
    $("#return_top").click(function() {
        $('html,body').animate({
            scrollTop: 0
        }, 1000);
        return false;
    });

    // search
    $("#searchSubmitButton").click(function(){
        var searchData=document.getElementById("searchData");
        searchData.submit();
    });
    // select suggestion
    $(window).keyup(function(e){
        if (e.keyCode==38&&searchSugNum==-1) {
            return;
        };
        eveCode=e.keyCode;
        selectSearchSug(e.keyCode);
    });
    $(".searchSuggestions").on("mouseover",".searchSuggestionsList",function(){
        $(".searchSuggestionsList").removeClass("activeSug");
        $(this).addClass("activeSug");
        searchSugNum=$(".searchSuggestionsList").index($(this));
    });
    $("#mainSearchBox").on("mouseover","#keyWord",function(){
        $(".searchSuggestionsList").removeClass("activeSug");
        searchSugNum=-1;
        $(this).focus();
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
    });
    $("#message").mouseover(function() {
        $("#msgNum").css({
            "background": "pink",
            "color": "darkred",
            "box-shadow": "#FFF"
        });
    });
    $("#message").mouseleave(function() {
        $("#msgNum").css({
            "background": "pink",
            "color": "#680",
            "box-shadow": "#AAA"
        });
    });

    // login&register
    $("#loginSubmitButton").click(function() {
        loginSubmit();
    });
    $("#registerSubmitButton").click(function() {
        registerSubmit();
    });
    // quick login&register
    $("#loginPassword").bind({
        focus:function() {
                isLoginPasswordFocus = true;
                $(window).keyup(function(e) {
                        var keyCode = e.keyCode;
                        if (keyCode == 13 && isLoginPasswordFocus) {
                            loginSubmit();
                        }
                        return false;
                    });
                },
        blur:function() {
                isLoginPasswordFocus = false;
            }
    });
    $("#registerRepassword").bind({
        focus:function() {
                    isRegisterRepasswordFocus = true;
                    $(window).keyup(function(e) {
                        var keyCode = e.keyCode;
                        if (keyCode == 13 && isRegisterRepasswordFocus) {
                            registerSubmit();
                        }
                        return false;
                    });
                },
        blur:function() {isRegisterRepasswordFocus = false;}
    });

    // change login&register
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

    // logout
    $("#logout").click(function() {
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

    // loginBox&registerBox show
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
    $("#myCollection").click(function() {
        var url = '/u/collection';
        $.getJSON(url, function(data) {
            console.log(data);
            return;
            $(".myCollectionList").remove();
            renderTemplateAfter('#collection-template', newColl);
        });
        $(".myCollectionWarp").animate({
            height:$(".myCollection").innerHeight()
        }, function() {
            $(".myCollection").fadeIn(500);
            $(".myCollectionWarp").css("height","auto");
        });
        return false;
    });
    $("#myCollectionBack").click(function() {
        $(".myCollection").fadeOut(500, function() {
            $(".myCollectionWarp").animate({
                height: 0
            });
        });
        return false;
    });
    $(".myCollectionClassButton").click(function(){
        var indexOfCollBut=$(".myCollectionClassButton").index($(this));
        console.log(indexOfCollBut);
        if ($(".myCollectionCon").eq(indexOfCollBut).css("display")!="none") {
            return false;
        };
        $(".myCollectionCon").hide();
        $(".myCollectionCon").eq(indexOfCollBut).show();
        return false;
    });

    // my note
    $("#myNote").click(function() {
        $(".myNoteWrap").animate({
            height: 415
        }, function() {
            $(".myNote").fadeIn(500);
            $.getJSON("/u/memo",function(data){
                var err = getError();
                if (err) {
                    showError("获取便笺失败");
                    return;
                }
                $(".myNoteListWrap").empty();
                if (data.length == undefined) {
                    $("#deleteCurrentNote,#saveCurrentNote").hide();
                    $("#createNewNote").show();
                    return false;
                } else {
                    data.forEach(function(item) {
                        renderTemplateAppend('#memo-template', item, '.myNoteListWrap');
                    });
                    var noteNum=data.length-1;
                    activeNoteID=data[0].id;
                    $(".myCurrentNoteTitle").val(data[noteNum].title);
                    $(".myCurrentNoteContent").val(data[noteNum].content);
                    // TODO: server sent the proper time
                    $(".myCurrentNoteTime").text(data[noteNum].create_time.slice(0,10));
                    $("#No_memo_"+activeNoteID).addClass("activeMyNoteList");
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
    // preparation for adding note
    $("#addNote").click(function(){
        $(".myCurrentNoteTitle").val("").focus();
        $(".myCurrentNoteContent").val("");
        $(".myCurrentNoteTime").text("");
        $("#deleteCurrentNote,#saveCurrentNote").hide();
        $("#createNewNote").show();
        $(".myNoteList").removeClass("activeMyNoteList");
        $("#addNote").addClass("activeMyNoteList").text("创建中...");
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
                showError("便笺创建失败",2000);
                return;
            }
            var newNote = JSON.parse(data);
            activeNoteID = newNote.id
            $(".myNoteListWrap").prepend(renderTemplateString('#memo-template',newNote));
            $(".myCurrentNoteTitle").val(newNote.title);
            $(".myCurrentNoteContent").val(newNote.content);
            $(".myCurrentNoteTime").text(newNote.create_time.slice(0,10));
            $("#deleteCurrentNote,#saveCurrentNote").show();
            $("#createNewNote").hide();
            $(".myNoteList").removeClass("activeMyNoteList");
            $("#No_memo_"+activeNoteID).addClass("activeMyNoteList");
            $("#addNote").text("创建便笺");
        });
    });
    // save note
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
                showError("保存便笺失败");
                return;
            }
            showError("成功保存便笺");
            $("#No_memo_"+activeNoteID).text($(".myCurrentNoteTitle").val());
            activeNoteID=parseInt($(".myNoteList").eq(0).attr("id").slice(8));

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
                showError("便笺删除失败");
                return;
            }
            $("#No_memo_" + activeNoteID).removeClass("activeMyNoteList").remove();
            activeNoteID=parseInt($(".myNoteList").eq(1).attr("id").slice(8));
            $(".myNoteList").eq(1).addClass("activeMyNoteList");

            $.getJSON("/u/memo?id="+activeNoteID,function(data){
                var err =getError(data);
                if (err) {
                    showError("更新便笺失败",2000);
                    return;
                }else{
                    $(".myCurrentNoteTitle").val(data.title);
                    $(".myCurrentNoteContent").val(data.content);
                    $(".myCurrentNoteTime").text(data.create_time.slice(0,10));
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

    // my setting
    $("#setting").click(function(){
        $(".mySettingWrap").animate({
            height:$(".mySetting").innerHeight()
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

    // image upload back
    $("#uploadImageBack").click(function(){
        $("section#main,#uploadImageBack,#info_zone,.mask").hide();
        return false;
    })

    $("#loginUsername").bind('input', lengthLimit(30));
    $("#registerUsername").bind('input', lengthLimit(30));
    $("#registerPassword").bind('input', lengthLimit(30));
    $("#registerRepassword").bind('input', lengthLimit(30));

    $(".communication").on("click",".topicOutter .topicTalkContent img",function(){
        var imgUrl=$(this).attr("src");
        showBigImage(imgUrl);
        return false;
    });
    $(".groupDynamic").on("click",".groupDynamicBrief img",function(){
        var imgUrl=$(this).attr("src");
        showBigImage(imgUrl);
        return false;
    });
    $("#bigImageBack,.bigImage img").click(function(){
        $(".mask,.bigImage,#bigImageBack").hide();
        return false;
    });
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
    checkEmailExist(loginUsername,function(b){
        if (!b) { checkUsernameExist(loginUsername,function(b){
                if (!b) { showError("邮箱或用户名不存在");return false;
                };
            });
        };
    });
    loginAction(loginUsername, loginPassword);
}

function loginAction(loginUsername,loginPassword){
    $.post("/login", {
        username: loginUsername,
        password: loginPassword
    }, function(data) {
        var err = getError(data);
        if (err) {
            showError("密码错误",2000);
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
        showError(errmsg, 2000);
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

function checkUsernameExist(username,callback){
    $.getJSON("/account?check_username&v=" + username, function(data) {
        if (data.msg == 1) {
            callback(true);
        } else if (data.msg == 0){
            callback(false);
        }
    });
}

function checkEmailExist(email,callback){
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
    } else if (username.length==0) {
        setError("用户名长度不能为空");
    } else if (username.length > 20) {
        setError("用户名请限定在20字以内");
    } else {
        return true;
    }
    return false;
}

function checkPassword(password,repassword){
    if (password.length < 2) {
        showError("密码长度不能小于2位",2000);
    } else if (password.length > 30) {
        showError("密码长度不能超过30",2000);
    } else if (password!=repassword) {
        showError("两次密码不一致",2000);
    } else {
        return true;
    }
    return false;
}

function checkEmail(email){
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (re.test(email)) {
        return true;
    }else if (email=="") {
        showError("Email不能为空");
        return false;
    } else {
        showError("Email地址不合法",2000);
        return false;
    }
    return false;
}

function registerSubmit() {
    var username = $("#registerUsername").val();
    var password = $("#registerPassword").val();
    var repassword = $('#registerRepassword').val();
    var email = $("#registerEmail").val();

    if (!(checkUsername(username) && checkEmail(email) && checkPassword(password,repassword))) {
        return;
    };

    checkUsernameExist(username, function(b) {
        if (b){
            console.log("aaa"+b);
            showError("用户名 "+username+" 已存在",2000);
            return;
        }
    });

    checkEmailExist(email,function(b){
        if (b) {
            showError("该邮箱已存在",2000);
            return;
        };
    });
    $.post("/register", {
        nickname: username,
        password: password,
        email: email
    }, function(data) {
        var err = getError(data);
        if (err) {
            showError("注册失败");
        } else {
            showError("欢迎加入梧桐, " + username + "!<br>目前是测试期间，不需要邮箱激活~",5000);
            loginAction(username, password);
            registerBoxFade();
        }
    });
}

function testTremble() {
    $("#msgNum").html(parseInt($("#msgNum").text()) + 1);
    // document.getElementById("msgNum").innerHTML = parseInt($("#msgNum").text()) + 1;
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
                if (location.pathname.slice(0,9)=="/a/create") {
                    showError("未登入");
                };
                return;
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
    $("#No_memo_"+noteID).addClass("activeMyNoteList");
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

    if (eveCode==40||eveCode==38) {
        return;
    };
    if (searchKeyWord.replace(/\s/g,"").length==0&&searchKeyWord!="") {
        return;
    };

    $(".searchSuggestions").empty();
    searchSugNum=-1;

    // test search searchSuggestion
    if (searchKeyWord=="") {
        $(".searchSuggestions").addClass("noBorderBottom");
        if (location.pathname=="/home.html") {
            $("#quickBrowse").html("浏 览").css("font-size","1.5em");
            $("#quickCreate").html("创 作").css("font-size","1.5em");
            $("#quickGroup").html("小 组").css("font-size","1.5em");
        };
        return;
    };
    $(".searchSuggestions").removeClass("noBorderBottom");
    var returnWordsNum=Math.floor(Math.random()*8)+2;
    for(var i=0;i<returnWordsNum;i++){
        var searchSuggestionWord=searchKeyWord+generateMixed(2);
        var app='<a class="searchSuggestionsList" href="/search/'+searchSuggestionWord+'" >'+searchSuggestionWord+'</a>';
        $(".searchSuggestions").prepend(app);
    };

    // in home page
    if (location.pathname=="/home.html") {
        $("#quickBrowse").html("选择与 <span class='searchKeyWord'>"+searchKeyWord+"</span> <br>最相关的作品阅读").css("font-size","0.8em");
        $("#quickCreate").html("以 <span class='searchKeyWord'>"+searchKeyWord+"</span> <br>为标题开始作品创作").css("font-size","0.8em");
        $("#quickGroup").html("进入以 <span class='searchKeyWord'>"+searchKeyWord+"</span> <br>为名的小组").css("font-size","0.8em");
    };
}

function selectSearchSug(keyCode){
    if (keyCode==40&&searchSugNum==-1) {
        searchSugNum+=1;
        $(".activeSug").removeClass("activeSug");
        $(".searchSuggestions").children().eq(searchSugNum).addClass("activeSug");
        $("#keyWord").blur();
    }else if (keyCode==40&&(searchSugNum+1)!=$(".searchSuggestions").children().size()) {
        searchSugNum+=1;
        $(".activeSug").removeClass("activeSug");
        $(".searchSuggestions").children().eq(searchSugNum).addClass("activeSug");
    }else if (keyCode==38&&searchSugNum!=0) {
        searchSugNum-=1;
        $(".activeSug").removeClass("activeSug");
        $(".searchSuggestions").children().eq(searchSugNum).addClass("activeSug");
    }else if (keyCode==38&&searchSugNum==0) {
        searchSugNum-=1;
        $(".activeSug").removeClass("activeSug");
        $("#keyWord").focus();
    };
    return;
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
    return innerHTML;
}

function renderTemplateAppend(temp, obj, target) {
    var innerHTML = renderTemplateString(temp, obj);
    if (target) {
        $(target).append($(innerHTML));
    } else {
        $(temp).append($(innerHTML));
    }
    return innerHTML;
}

function renderTemplatePrepend(temp, obj, target) {
    var innerHTML = renderTemplateString(temp, obj);
    if (target) {
        $(target).prepend($(innerHTML));
    } else {
        $(temp).prepend($(innerHTML));
    }
    return innerHTML;
}

function showBigImage(url){
    $(".mask").show();
    $(".bigImage img,.preBigImage img").attr("src",url);
    var imgDomWidth=document.getElementById("preBigImageCon").width;
    console.log(imgDomWidth);
    var imgHeight=$(".preBigImage img").height();
    console.log(imgHeight,$(window).height());
    if (imgHeight<$(window).height()) {
        var marginTop=($(window).height()-imgHeight)/2;
        console.log(marginTop);
        $(".bigImage img").css({"margin-top":marginTop+"px"});
    }else{
        $(".bigImage img").css({"margin-top":"0px"});
    }
    $(".bigImage").fadeIn();
}

function scrollLoading(loadEle){
    var top=$(window).scrollTop();
    var buttom=top+$(window).height();
    var opusTop=$(loadEle).scrollTop();
    var opusButtom=opusTop+$(loadEle).height();
    if(buttom>opusButtom&&($(loadEle).has(".loadingBox").length==0)){
        loadingShow(loadEle);
        // $
    };
    return false;
}

function loadingShow(loadEle){
    // var loadingBox=$(".loadingBoxWrap").html();
    // $(loadEle).append(loadingBox);
}

function loadingHide(loadEle){
    $(loadEle).children(".loadingBox").remove();
}

function initPage(p){
    var pageOut={
        pageInfo:'<span class="pageInfo">共'+p.pageNum+'页/'+p.BCNum+'条'+p.turnType+'</span>',
        firstPage:'<a href="javascript:(0)" onclick="turnPage(1,'+"'"+p.turnEle+"'"+')">首页</a>',
        lastPage:'<a href="javascript:void(0)" onclick="turnPage('+p.pageNum+','+"'"+p.turnEle+"'"+')">末页</a>',
        prePage:'<a href="javascript:void(0)" onclick="turnPage('+(p.thisPageNum-1)+','+"'"+p.turnEle+"'"+')">上一页</a>',
        nextPage:'<a href="javascript:void(0)" onclick="turnPage('+(p.thisPageNum+1)+','+"'"+p.turnEle+"'"+')">下一页</a>'
    };
    var turnContainer=$(p.turnBox);
    turnContainer.addClass("turnContainer");
    turnContainer.empty();
    if (p.BCNum==0) {
        turnContainer.append("<span class='noBC'>目前还没有任何"+p.turnType+"呢</span>");
        return false;
    };
    if (p.pageNum==1) {
        return false;
    };
    if (p.pageNum<=10) {
        turnContainer.append(pageOut.pageInfo);
        for(var i=1;i<=p.pageNum;i++){
            forThisPage();
        };
        if (p.pageNum!=1) {
            if (p.thisPageNum!=p.pageNum) {
                turnContainer.append(pageOut.nextPage);
            };
        };
        return false;
    };
    if (p.thisPageNum<(p.pageNum-5)&&p.thisPageNum<=5) {
        turnContainer.append(pageOut.pageInfo);
        if (p.thisPageNum!=1) {
            turnContainer.append(pageOut.firstPage);
        };
        for(var i=1;i<=10;i++){
            forThisPage();
        };
        if (p.thisPageNum!=p.pageNum) {
            turnContainer.append(pageOut.nextPage);
            turnContainer.append(pageOut.lastPage);
        };
        return false;
    };
    if (p.thisPageNum<(p.pageNum-5)) {
        turnContainer.append(pageOut.pageInfo);
        turnContainer.append(pageOut.firstPage);
        for(var i=(p.thisPageNum-4);i<=(p.thisPageNum+5);i++){
           forThisPage();
        };
        if (p.thisPageNum!=p.pageNum) {
            turnContainer.append(pageOut.nextPage);
            turnContainer.append(pageOut.lastPage);
        };
        return false;
    };
    turnContainer.append(pageOut.pageInfo);
    turnContainer.append(pageOut.firstPage);
    if ((p.thisPageNum+5)<p.pageNum) {
        for(var i=(p.thisPageNum-4);i<=p.pageNum;i++){
            forThisPage();
        };
    }else{
        var minus=p.pageNum-p.thisPageNum;
        for(var i=(p.thisPageNum-(9-minus));i<=p.pageNum;i++){
            forThisPage();
        };
    }
    if (p.thisPageNum!=p.pageNum) {
        turnContainer.append(pageOut.nextPage);
        turnContainer.append(pageOut.lastPage);
    };

    function forThisPage(){
        if (i==p.thisPageNum) {
            turnContainer.append('<a href="javascript:void(0)" onclick="turnPage('+i+','+"'"+p.turnEle+"'"+')" class="HLThisPage">'+i+'</a>');
        }else{
            turnContainer.append('<a href="javascript:void(0)" onclick="turnPage('+i+','+"'"+p.turnEle+"'"+')">'+i+'</a>');
        }
    }
    return false;
}

function turnPage(i,turnEle){
    var op={
        pageNum:p.pageNum,
        BCNum:p.BCNum,
        thisPageNum:i,
        turnEle:p.turnEle,
        turnBox:p.turnBox,
        turnType:p.turnType
    };
    initPage(op);
    return false;
}


String.prototype.httpHtml = function() {
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-|:)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}

Array.prototype.remove = function(value){
    for(b in this){
        if(this[b] == value){
            this.splice(b,1);
            break;
        }
    }
    return this;
}

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

Array.prototype.intersect = function(b) {
    var a = this;
    var ai=0, bi=0;
    var result = new Array();

    while( ai < a.length && bi < b.length )
    {
        if      (a[ai] < b[bi] ){ ai++; }
        else if (a[ai] > b[bi] ){ bi++; }
        else /* they're equal */
        {
            result.push(a[ai]);
            ai++;
            bi++;
        }
    }
    return result;
}
