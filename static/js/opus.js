var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var topOfSight=100;

$(document).ready(function(){
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

    // $("#return_top").click(function(){
    //     $('html,body').animate({scrollTop:0},300);
    //     return false;
    // });

    // var mainTextChildren=$(".opusMain").children();

    $(window).scroll(function(){
        var top=$(window).scrollTop();
        var buttom=top+$(window).height();
        // if(top>200){
        //     var realHeight=(top+(window.screen.availHeight)/2)+'px';
        //     $('#return_top').removeClass('none');
        //     $('#return_top').stop();
        //     $('#return_top').animate({top:realHeight},500);
        // }
        // else{
        //     $('#return_top').addClass('none');
        // }

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
                   ( (offsetHeightOfOpusMainChild>=(top+topOfSight)&&offsetHeightOfOpusMainChild<(top+topOfSight+20)) )||
                   ( (offsetHeightOfOpusMainChild<=(top+topOfSight)&&((offsetHeightOfOpusMainChild+heightOfOpusMainChild))>(top+topOfSight+20) )) 
                )&&($(".opusSideCommentList"+i).css("display")!="none")
                   ){
                    $(".opusSideComment").stop();
                    $(".opusMain").children().css({"color":"rgb(68,68,68)","opacity":"1.0"});
                    $(".opusMain").children().eq(i).css({"color":"#680","opacity":"0.7"});
                    var heightOfSideCommnetChild=$(".opusSideCommentList"+i).eq(0).position().top + $(".opusSideComment").scrollTop();
                    $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
                    $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
                    $(".opusSideComment").children((".opusSideCommentList"+i)).addClass("activeOpusSideCommentList");
                    $(".opusSideCommentList"+i).eq(0).removeClass("activeOpusSideCommentList").addClass("activeOpusSideCommentNav");
                    $(".opusSideComment").animate({scrollTop:heightOfSideCommnetChild},1000);
                }
            };
        };  
        $(".nullOpusSideCommentNav").css("display","none");
        return false;
    })

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

    $("#expandSideComment").click(function(){
        if ($(".opusSideCommentWrap").css("display")=="none") {
            expandSideComment();
        }else{
            foldSideComment();
        }
    })

    $(".opusMain").children().mouseover(function(){
        if ($(".opusSideCommentWrap").css("display")!="none"){
            $(this).children(".sideCommentView,.sideCommentEdit").fadeIn(50);
        }
    });
    $(".opusMain").children().mouseleave(function(){
        if ($(".opusSideCommentWrap").css("display")!="none"){
            $(this).children(".sideCommentView,.sideCommentEdit").fadeOut(50);
        }
    })

    $(".sideCommentView").click(function(){
        $(".nullOpusSideCommentNav").css("display","none");
        var indexOfPara=$(".sideCommentView").index($(this)).toString();
        $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
        $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
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

});

function init(){
    for(var i=0;i<25;i++){
        var numOfComment=Math.floor(3*Math.random());
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
        }
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
    }
    for (var i =0; i<$(".opusMain").children().size(); i++) {
        var viewCommentButton='<a href="#" class="sideCommentView">查看评论</a><a href="#" class="sideCommentEdit">编辑评论</a>';
        $(".opusMain").children().eq(i).append(viewCommentButton);
    }
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
    $(".opusSideCommentWrap").removeClass("noTransition");
    $(".readMain").addClass("floatReadMain");
    $(".read").css({"width":"100%"});
    var widthOfSideComment=($(window).width()-$(".floatReadMain").width()-42);
    $(".opusSideComment").css({"height":(visibleHeght()+"px"),"width":widthOfSideComment+"px"});
    $(".opusSideCommentList").css({"width":(widthOfSideComment-40)+"px"});
    $(".opusSideCommentWrap").fadeIn();
    $("#expandSideComment").text("收起侧评");
}

function foldSideComment(){
    $(".opusSideCommentWrap").addClass("noTransition");
    $(".opusSideCommentWrap").fadeOut();
    $(".readMain").removeClass("floatReadMain");
    $(".read").css({"width":"1060px"});
    $(".opusMain").children().css({"color":"rgb(68,68,68)","opacity":"1.0"});
    $(".sideCommentView,.sideCommentEdit").hide();
    $("#expandSideComment").text("展开侧评");
}