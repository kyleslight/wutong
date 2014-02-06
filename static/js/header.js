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

highlightThisPage();

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
            $("#myHomepage").parent().attr("href","/user/"+username);
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
            // TODO: deal create_time
            renderById('collection-template', data);
        });
        $(".myCollectionWarp").animate({
            height: heightOfMycollection
        }, function() {
            $(".myCollection").fadeIn(500);
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
        document.getElementsByClassName("myCurrentNoteTitle")[0].focus();
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
            $(".myNoteListWrap").empty();
            $(".myCurrentNoteTitle").val("");
            $(".myCurrentNoteContent").val("");
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
    });

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
    if (location.pathname === '/g/browse')
        window.location = location.pathname;
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
                    $("#myHomepage").parent().attr("href","/user/"+username);
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

function showError(errorStatement,duration){
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

function renderById(idstr, jsondata) {
    var id = '#' + idstr;
    var template = $(id).html();
    var innerHTML = Mark.up(template, jsondata);
    $(id).after($(innerHTML));
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

var testLoadTime=0;
function scrollLoading(loadEle){
    if (testLoadTime>3) {
        return false;
    };
    if (testLoadTime==3) {
        loadingHide(loadEle);
        $(loadEle).append("<div class='testLoadContent'>再怎么找也没有啦╮(￣▽￣)╭</div>");
        testLoadTime+=1;
        return false;
    };
    var top=$(window).scrollTop();
    var buttom=top+$(window).height();
    var opusTop=$(loadEle).scrollTop();
    var opusButtom=opusTop+$(loadEle).height();
    if(buttom>opusButtom&&($(loadEle).has(".loadingBox").length==0)){
        loadingShow(loadEle);
        setTimeout(function(){
            $(loadEle).append($(loadEle).children().clone());
            testLoad(loadEle);
        },2000);
    };
    return false;
}

function loadingShow(loadEle){
    var loadingBox=$(".loadingBoxWrap").html();
    $(loadEle).append(loadingBox);
}

function loadingHide(loadEle){
    $(loadEle).children(".loadingBox").remove();
}

function testLoad(loadEle){
    loadingHide(loadEle);
    testLoadTime+=1;
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
