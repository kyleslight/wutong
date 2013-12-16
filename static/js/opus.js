var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var topOfSight=150;

$(document).ready(function(){
    // initializing the opus and side commnet
    init();

    $.getJSON("/u/info", function (data) {
        var username;
        console.log(data);
        username = data.penname;
        $(".navrightoff").fadeOut(10,function(){
            $(".navrighton").fadeIn(10);
            $("#username").children().val(username);
            $("#usernameHover").text(username);
        });
    });

    // scroll event
    $(window).scroll(function(){
        var top=$(window).scrollTop();
        var buttom=top+$(window).height();

        // reset sidecoment position
        if ((top)>$(".readMain").offset().top) {
            $(".opusSideCommentWrap").css({"top":"0px","position":"fixed","float":"none","right":"0px"});
        }else{
            $(".opusSideCommentWrap").css({"position":"relative","float":"right"});
        }

        // set height of side comment
        $(".opusSideComment").css({"height":(visibleHeght()+"px")});

        // side comment scroll with the sight of user 
        if ($(".opusSideCommentWrap").css("display")!="none") {
            for (var i =0; i<$(".opusMain").children().size(); i++) {
                var offsetHeightOfOpusMainChild=$(".opusMain").children().eq(i).offset().top;
                var heightOfOpusMainChild=$(".opusMain").children().eq(i).height();
                if(
                (
                   ( (offsetHeightOfOpusMainChild>=(top+topOfSight)&&offsetHeightOfOpusMainChild<(top+topOfSight+60)) )||
                   ( (offsetHeightOfOpusMainChild<=(top+topOfSight)&&((offsetHeightOfOpusMainChild+heightOfOpusMainChild))>(top+topOfSight+5) )) 
                )
                &&($(".opusSideCommentList"+i).css("display")!="none")
                   ){
                    $(".opusSideComment").stop();
                    $(".activeOpusPara").removeClass("activeOpusPara");
                    $(".opusMain").children().eq(i).addClass("activeOpusPara");
                    var heightOfSideCommnetChild=$(".opusSideCommentList"+i).eq(0).position().top + $(".opusSideComment").scrollTop();
                    $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
                    $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
                    $(".opusSideComment").children((".opusSideCommentList"+i)).addClass("activeOpusSideCommentList");
                    $(".opusSideCommentList"+i).eq(0).removeClass("activeOpusSideCommentList").addClass("activeOpusSideCommentNav");
                    $(".opusSideComment").animate({scrollTop:heightOfSideCommnetChild},1000);
                }else if (
                    (
                        ( (offsetHeightOfOpusMainChild>=(top+topOfSight)&&offsetHeightOfOpusMainChild<(top+topOfSight+60)) )||
                        ( (offsetHeightOfOpusMainChild<=(top+topOfSight)&&((offsetHeightOfOpusMainChild+heightOfOpusMainChild))>(top+topOfSight+5) )) 
                    )
                        &&($(".opusSideCommentList"+i).css("display")=="none")
                    ) {
                    $(".activeOpusPara").removeClass("activeOpusPara");
                    $(".opusMain").children().eq(i).addClass("activeOpusPara");
                    $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
                    $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
                };
            };
        };
        // when user scroll,if the side comment is null,it will fade
        $(".nullOpusSideCommentNav").css("display","none");

        return false;
    })
    
    // expand or flod buttom comment
    $(".opusCommentIntro a").click(function(){
        if ($(".opusCommentList").css("display")=="none") {
            $(this).text("收起底部评论");
            $(".opusCommentList").show();
            var heightOfReadMain=($(".floatReadMain").height()+40)+"px";
            $(".opusSideCommentWrap").css({"height":heightOfReadMain});

        }else{
            $(this).text("展开底部评论");
            $(".opusCommentList").hide();
            $('#return_top').css({"top":"1200px"});
            var heightOfReadMain=($(".floatReadMain").height()+40)+"px";
            $(".opusSideCommentWrap").css({"height":heightOfReadMain});
        }
        
        return false;
    })

    // expand or fold side comment
    $("#expandSideComment").click(function(){
        if ($(".opusSideCommentWrap").css("display")=="none") {
            expandSideComment();
        }else{
            foldSideComment();
        }
    })

    // show and fade option of opus para
    $(".opusMain").children().mouseover(function(){
        if ($(".opusSideCommentWrap").css("display")!="none"){
            $(this).children(".sideCommentView,.sideCommentEdit").fadeIn(100);
        }
    });
    $(".opusMain").children().mouseleave(function(){
        if ($(".opusSideCommentWrap").css("display")!="none"){
            $(this).children(".sideCommentView,.sideCommentEdit").fadeOut(10);
        }
    });

    // view the side comment of this para
    $(".sideCommentView").click(function(){
        $(".nullOpusSideCommentNav").css("display","none");
        var indexOfPara=$(".sideCommentView").index($(this)).toString();
        $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
        $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
        $(".activeOpusPara").removeClass("activeOpusPara");
        $(".opusMain").children().eq(indexOfPara).addClass("activeOpusPara");
        if ($(".opusSideCommentList"+indexOfPara).css("display")!="none") {
            var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
            $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});
            $(".opusSideComment").children((".opusSideCommentList"+indexOfPara)).addClass("activeOpusSideCommentList");
            $(".opusSideCommentList"+indexOfPara).eq(0).removeClass("activeOpusSideCommentList").addClass("activeOpusSideCommentNav");
        }else{
            $(".opusSideCommentList"+indexOfPara).eq(0).fadeIn(500,function(){
                var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
                $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});       
            });     
        }
        return false;
    })
    
    // edit the side comment of this para
    $(".sideCommentEdit").click(function(){
        var indexOfPara=$(".sideCommentEdit").index($(this));
        var buttomOfActivePara=$(".opusMain").children().eq(indexOfPara).offset().top+$(".opusMain").children().eq(indexOfPara).height()-60;
        $(".sideCommentEditBox").css({"top":buttomOfActivePara+"px"});
        $(".sideCommentEditBox").fadeIn(100);
        $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
        $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
        $(".activeOpusPara").removeClass("activeOpusPara");
        $(".opusMain").children().eq(indexOfPara).addClass("activeOpusPara");
        if ($(".opusSideCommentList"+indexOfPara).css("display")!="none") {
            var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
            $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});
            $(".opusSideComment").children((".opusSideCommentList"+indexOfPara)).addClass("activeOpusSideCommentList");
            $(".opusSideCommentList"+indexOfPara).eq(0).removeClass("activeOpusSideCommentList").addClass("activeOpusSideCommentNav");
        }else{
            $(".opusSideCommentList"+indexOfPara).eq(0).fadeIn(500,function(){
                var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
                $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});       
            });     
        };
        var sideCommentEditFocus = document.getElementById("sideCommentEditData");
                sideCommentEditFocus.focus();
        return false;
    });

    // fade the edit area
    $("#sideCommentEditBack").click(function(){
        $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
        $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
        $(".activeOpusPara").removeClass("activeOpusPara");
        $(".sideCommentEditBox").fadeOut(100);
        $("#sideCommentEditData").val("");
        return false;
    });

    // send editting side comment
    $("#sideCommentEditSend").click(function(){
        var contentOfEdittingSideComment=$("#sideCommentEditData").val();
        console.log(contentOfEdittingSideComment);
    })

});

function init(){
    for(var i=0;i<25;i++){
        var numOfComment=Math.floor(20*Math.random());
        var appNav='<li class="opusSideCommentList opusSideCommentList'+i+' opusSideCommentNav" >'
                    +'第'+i+'段评论('+'<span class="numOfParaComent">'+numOfComment+'</span>'+')'
                    +'</li>';
        var appNull='<li class="opusSideCommentList opusSideCommentList'+i+' opusSideCommentNav nullOpusSideCommentNav" >'
                    +'这个段落目前还没有评论，你可以通过“编辑评论”开始创建'
                    +'</li>';
        if (numOfComment!=0) {
            $(".opusSideComment").append(appNav);
        }else{
            $(".opusSideComment").append(appNull);
        };
        for(var j=0;j<numOfComment;j++){
            var appText='<li class="opusSideCommentList opusSideCommentList'+i+'" >'
                    +   '<a href="#" class="opusSideCommentListUserName">kyleslight</a>'
                    +   '<div class="opusSideCommentContent">'
                    +       'lalallalal<br/>'
                    +       'lalallallalla<br/>'
                    +       'lalallal<br/>'
                    +       'lalallasdjfhjsdhf'
                    +   '</div>'
                    +'</li>';
            $(".opusSideComment").append(appText);
        }
    };
    for (var i =0; i<$(".opusMain").children().size(); i++) {
        var viewCommentButton='<a href="#" class="sideCommentView">查看评论</a><a href="#" class="sideCommentEdit">编辑评论</a>';
        $(".opusMain").children().eq(i).append(viewCommentButton);
    };
    $(".opusMain").children().addClass("opusMainChildren");
}

function topPartHeight(){
    var top=$(window).scrollTop();
    var buttom=top+$(window).height();
    if(($(".readMain").offset().top-top)>0){
        return $(".readMain").offset().top-top;
    };
    return 0;
}

function buttomPartHeight(){
    var top=$(window).scrollTop();
    var buttom=top+$(window).height();
    if ((buttom-($(".readMain").offset().top+$(".readMain").height()))>0) {
        return buttom-($(".readMain").offset().top+$(".readMain").height());
    };
    return 0;
}

function visibleHeght(){
    if (buttomPartHeight()==0) {
       return $(window).height()-(topPartHeight()+buttomPartHeight()); 
    };
    return $(window).height()-(topPartHeight()+buttomPartHeight())+40;
}

function expandSideComment(){
    var top=$(window).scrollTop();
    $(".opusSideCommentWrap").removeClass("noTransition");
    $(".readMain").addClass("floatReadMain");
    $(".read").css({"width":"100%"});
    var widthOfSideComment=($(window).width()-$(".floatReadMain").width()-47);
    $(".opusSideComment").css({"height":(visibleHeght()+"px"),"width":widthOfSideComment+"px"});
    $(".opusSideCommentList").css({"width":(widthOfSideComment-45)+"px"});
    $(".opusSideCommentWrap").fadeIn();
    $("#expandSideComment").text("收起侧评");
    $('html,body').animate({scrollTop:top},1000);
    // $('html,body').scrollTop(top);
}

function foldSideComment(){
    $("#expandSideComment").text("展开侧评");
    $(".opusSideCommentWrap").fadeOut(50);
    $(".activeOpusPara").removeClass("activeOpusPara");
    $(".opusMain").children().removeClass("activeOpusPara");
    $(".opusMain").children().css({"color":"rgb(68,68,68)","opacity":"1.0"});
    var top=$(window).scrollTop();    
    $(".readMain").removeClass("floatReadMain");
    $(".read").css({"width":"1060px"});
    $('html,body').animate({scrollTop:top},500,function(){
        $(".activeOpusPara").removeClass("activeOpusPara");
    });
    $(".sideCommentView,.sideCommentEdit").hide();
    $(".opusSideCommentWrap").addClass("noTransition");
}