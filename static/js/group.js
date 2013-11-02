var isLoginBox=false;
var isRegisterBox=false;
var isOtherOptionShow=false;
var activeIndex=-1;
var elapseTime = 4500;
var shortElapseTime=4000;
var _showwel_flag = true;
var _last_post_id;

$(document).ready(function(){
    //check sex of the member
    renderMaleAndFemale();
    // $.getJSON("/foo", function (data) {
    //     data.groupName;
    // });

    $("#loginSubmitButton").click(function() {
        var loginUsername=$("#loginUsername").val();
        var loginPassword=$("#loginPassword").val();
        $.post("/login", {
            username:loginUsername,
            password:loginPassword
        }, function (response) {
            if (response == "success") {
                // todo
            } else if (response == "failed") {

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
        $.post("/register",{
            username:registerUsername,
            password:registerPassword,
            email:registerEmail
        });
    });


    // login and register
    $("#login").click(function(){
        if (_showwel_flag == true){
            _showwel_flag = false;
            setTimeout(function() {
                _showwel_flag = true;
            }, elapseTime);
            if (isRegisterBox||isLoginBox) {
                $("#loginBox,#registerBox").fadeOut(100,function(){
                    $("#lrBoxWrap").animate({height:"0px"},1000,function(){
                        $("#lrBoxWrap").fadeOut(200,function(){
                            loginBoxShow();
                        });
                    });
                })
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
                $("#loginBox,#registerBox").fadeOut(100,function(){
                    $("#lrBoxWrap").animate({height:"0px"},1000,function(){
                        $("#lrBoxWrap").fadeOut(200,function(){
                            registerBoxShow();
                        });
                    });
                });
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
                    $(this).slideUp(1000);
                        // $(this).removeClass("outOfView").addClass("none");
                    $("#groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").fadeIn(100,function(){

                        var prepareHeight=$("#groupOptionShow"+indexOfDetailItem).height()+32+"px";
                        // alert(prepareHeight);
                        $(".groupItem").animate({height:prepareHeight},1000,function(){
                            $("#groupOptionShow"+activeIndex).addClass("none");
                        });
                        $("#groupOptionShow"+indexOfDetailItem).animate({left:"0px"},1000,function(){
                            $(this).removeClass("prepare").addClass("active");
                            // isOtherOptionShow=false;
                            activeIndex=indexOfDetailItem;
                        });
                    });

                });
            }else{
                $("#groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").slideDown(1000);
                $(".groupItem").slideDown(1000);
                $("#groupOptionShow"+indexOfDetailItem).removeClass("prepare").addClass("active").animate({left:'0px'},1500);
                // isOtherOptionShow=true;
                activeIndex=indexOfDetailItem;
            }
            // if (isOtherOptionShow) {
            //     $(".groupOptionShow"+activeIndex).removeClass("active").addClass("outOfView");
            //     $(".groupOptionShow"+activeIndex).animate({left:"-960px"},1500,function(){$(this).fadeOut(100,function(){$(this).removeClass("outOfView").addClass("none");$(".groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").fadeIn(100,function(){$(".fourmOption").slideDown();});$(".groupOptionShow"+indexOfDetailItem).animate({left:"0px"},1500,function(){$(this).removeClass("prepare").addClass("active");});})});
            //     isOtherOptionShow=false;
            //     activeIndex=indexOfDetailItem;
            // }else{
            //     $(".groupOptionShow"+indexOfDetailItem).addClass("prepare").css("left","960px").fadeIn(100);
            //     $(".fourmOption").slideDown();
            //     if(indexOfDetailItem==2){
            //         $(".groupOptionShow"+indexOfDetailItem).removeClass("prepare").addClass("active");
            //         var memCard=$(".groupOptionShow"+indexOfDetailItem).toArray();
            //         for (var i = 1; i <= memCard.length; i++) {
            //             if (i%3==1) {memCard[i].addClass("firstList")};
            //             if (i%3==2) {memCard[i].addClass("secondList")};
            //             if (i%3==0) {memCard[i].addClass("thirdList")};
            //         };
            //         $(".firstList").animate({left:'0px'},500);
            //         $(".secondList").animate({left:'300px'},1000);
            //         $(".thirdList").animate({left:'600px'},1500)
            //     }else{
            //         $(".groupOptionShow"+indexOfDetailItem).removeClass("prepare").addClass("active").animate({left:'0px'},1500);
            //         isOtherOptionShow=false;
            //         activeIndex=indexOfDetailItem;
            //     }
            // }
            return false;
        }
    })
    // group item back
    $(".optionBack").click(function(){
        var indexOfOptionBack=$(".optionBack").index($(this));
        $("#groupOptionShow"+indexOfOptionBack).removeClass("active").addClass("outOfView");
        $("#groupOptionShow"+indexOfOptionBack).animate({left:"-960px"},1500,function(){
            $(".groupItem").slideUp(500,function(){
                $("#groupOptionShow"+indexOfOptionBack).removeClass("outOfView").fadeOut(100);
            });
            $(".bulletinCon").fadeOut(500);
        });
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

    // long polling
    setInterval(function(){
        topic_id = $("#communication li:first-child").attr("id");
        topic_id = topic_id ? topic_id.replace("topic_", "") : '0';
        _last_post_id = topic_id;

        $.ajax({
            type:"GET",
            dataType: "json",
            url: "/test",
            timeout: 80000,
            data: {
                topic_id: topic_id
            },
            success:function(data, textStatus){
                if (!data)
                    return;

                var len = data.length;
                for (var i = 0; i < len; i++) {
                    var entry = data[i];
                    if (parseInt(entry.id, 10) <= parseInt(_last_post_id, 10))
                        continue;
                    else
                        _last_post_id = entry.id;
                    entry.submit_time=entry.submit_time.toString().substring(5,19);
                    condata = $(condata);
                    var condata="<li id='topic_"+entry.id+"'>"+"<a href='#'><img src='static/css/image/test.png'/></a><div class='talkmain'><div class='username'><a href='#'>"+entry.ip+"</a></div><div class='talkcontent'>"+entry.content+"</div>    </div><div class='timeshow'>"+entry.submit_time+"</div></li>";
                    $("#communication").prepend(condata);
                }
            },
            error:function(XMLHttpRequest,textStatus,errorThrown){
                // just do nothing
            }
        });

        var thedata=$("#communication").children().size();
        if (thedata>30) {
            for (var i = 30; i < thedata; i++) {
                $("#communication").children("li").eq(i).remove();
            }
        }
    }, 70000);
});

// function for login and register
function loginBoxShow(){
    $("#lrBoxWrap").fadeIn(200);
    $("#lrBoxWrap").animate({height:"200px"},1000,function(){$("#loginBox").fadeIn(200,function(){isLoginBox=true;isRegisterBox=false;});});
}

function loginBoxFade(){
    $("#loginBox").fadeOut(200);
    $("#lrBoxWrap").animate({height:"0px"},1000,function(){$("#lrBoxWrap").fadeOut(500);});
}

function registerBoxShow(){
    $("#lrBoxWrap").fadeIn(200);
    $("#lrBoxWrap").animate({height:"330px"},1000,function(){$("#registerBox").fadeIn(200,function(){isRegisterBox=true;isLoginBox=false;});});
}

function registerBoxFade(){
    $("#registerBox").fadeOut(200);
    $("#lrBoxWrap").animate({height:"0px"},1000,function(){$("#lrBoxWrap").fadeOut(500);});
}

// function for submit data
function submitChatData(){
    if($("#chatData").val().length>140){
        alert("请保持字数在140字以内");
        return;
    }
    chatCon=$("#chatData").val().httpHtml();
    chatCon=chatCon.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");
    if(chatCon.length==0){
        alert("Please input content");
        return;
    }
    // var thedata=$(".communication").children().size();
    // if (thedata>30) {
    //     for (var i =30; i < thedata; i++) {
    //         $("#communication").children("li").eq(i).remove();
    //     }
    // }
    $.ajax({
        type:"POST",
        dataType:"json",
        url:"/test",
        timeout:80000,
        data:{
            content:chatCon
        },
        success:function(data,textStatus){
        }
    });
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
        if ($("#groupOptionShow"+i).hasClass("active")) {isOtherOptionShow=true;activeIndex=i};
    };
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
    return this.replace(reg, '<a href="$1$2">$1$2</a>');
}
