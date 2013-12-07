var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var lastTimeOffsetHeight=0;

$(document).ready(function(){
    initSideComment();
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
        for (var i =0; i<$(".opusMain").children().size(); i++) {
            var offsetHeightOfOpusMainChild=$(".opusMain").children().eq(i).offset().top;
            var heightOfOpusMainChild=$(".opusMain").children().eq(i).height();
            if(
               ( (offsetHeightOfOpusMainChild>=(top+200)&&offsetHeightOfOpusMainChild<(top+220)) )||
               ( (offsetHeightOfOpusMainChild<=(top+200)&&((offsetHeightOfOpusMainChild+heightOfOpusMainChild))>(top+220) )) ){
                $(".opusSideComment").stop();
                $(".opusMain").children().css({"color":"rgb(68,68,68)","opacity":"1.0"});
                $(".opusMain").children().eq(i).css({"color":"#680","opacity":"0.7"});
                var heightOfSideCommnetChild=$(".opusSideCommentList"+i).eq(0).position().top + $(".opusSideComment").scrollTop();
                $(".opusSideComment").children().css({"color":"black"});
                $(".opusSideComment").children((".opusSideCommentList"+i)).css({"color":"#680"});
                console.log(i);
                $(".opusSideComment").animate({scrollTop:heightOfSideCommnetChild});
            }
        };
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
            $(".readMain").addClass("floatReadMain");
            $(".opusSideCommentWrap").fadeIn();
            $(".read").css({"width":"100%"});
            var widthOfSideComment=($(window).width()-$(".floatReadMain").width()-42)+"px";
            $(".opusSideComment").css({"height":(visibleHeght()+"px"),"width":widthOfSideComment});
        }else{
            $(".readMain").removeClass("floatReadMain");
            $(".opusSideCommentWrap").fadeOut();
            $(".read").css({"width":"1060px"});
        }
    })

    $(".paraNum").click(function(){
        var indexOfPara=$(".paraNum").index($(this)).toString();
        var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
        $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});
        $(".opusSideComment").children().css({"color":"black"});
        $(".opusSideComment").children((".opusSideCommentList"+indexOfPara)).css({"color":"#680"});
        return false;
    })

});

function initSideComment(){
    for(var i=0;i<25;i++){
        for(var j=0;j<5;j++){
            var appText='<li class="opusSideCommentList opusSideCommentList'+i+'" >'
                    +   '第'+i+'段评论<br/>'
                    +   'lalallalal<br/>'
                    +   'lalallallalla<br/>'
                    +   'lalallal<br/>'
                    +   'lalallasdjfhjsdhf'
                    +'</li>';
            $(".opusSideComment").append(appText);
        }
    }
    for (var i =0; i<$(".opusMain").children().size(); i++) {
        var viewCommentButton='<a href="#" class="paraNum">'+i+'</a>';
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