var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var topOfSight=150;
var editingParaNum=-1;
var editableOpusChild=$(".opusMain").children("div,p,table,blockquote");

$(document).ready(function(){
    // initializing the opus and side commnet
    init();

    $.getJSON("/u/info", function (data) {
        var username;
        username = data.penname;
        $(".navrightoff").fadeOut(10,function(){
            $(".navrighton").fadeIn(10);
            $("#username").children("p").val(username);
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
            for (var i =0; i<editableOpusChild.size(); i++) {
                var offsetHeightOfOpusMainChild=editableOpusChild.eq(i).offset().top;
                var heightOfOpusMainChild=editableOpusChild.eq(i).height();
                if(
                (
                   ( (offsetHeightOfOpusMainChild>=(top+topOfSight)&&offsetHeightOfOpusMainChild<(top+topOfSight+60)) )||
                   ( (offsetHeightOfOpusMainChild<=(top+topOfSight)&&((offsetHeightOfOpusMainChild+heightOfOpusMainChild))>(top+topOfSight+5) ))
                )
                &&($(".opusSideCommentList"+i).css("display")!="none")
                   ){
                    $(".opusSideComment").stop();
                    $(".activeOpusPara").removeClass("activeOpusPara");
                    editableOpusChild.eq(i).addClass("activeOpusPara");
                    var heightOfSideCommnetChild=$(".opusSideCommentList"+i).eq(0).position().top + $(".opusSideComment").scrollTop();
                    $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
                    $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
                    $("#sideCommentNode"+i).children().addClass("activeOpusSideCommentList");
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
                    editableOpusChild.eq(i).addClass("activeOpusPara");
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
        if ($(".buttomComment").css("display")=="none") {
            $(this).text("收起底部评论");
            $(".buttomComment").show();
            var heightOfReadMain=($(".floatReadMain").height()+40)+"px";
            $(".opusSideCommentWrap").css({"height":heightOfReadMain});
            var url = location.pathname + '/comment/bottom';
            $.getJSON(url, function(data) {
                $(".buttomComment").prepend(data);
            });
        }else{
            $(this).text("展开底部评论");
            $(".buttomComment").hide();
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
    editableOpusChild.mouseover(function(){
        if ($(".opusSideCommentWrap").css("display")!="none"){
            $(this).children(".sideCommentView,.sideCommentEdit").fadeIn(100);
        }
    });
    editableOpusChild.mouseleave(function(){
        if ($(".opusSideCommentWrap").css("display")!="none"){
            $(this).children(".sideCommentView,.sideCommentEdit").fadeOut(10);
        }
    });

    // view the side comment of this para
    $(".sideCommentView").click(function(){
        // clear nullOpusSideCommentNav
        $(".nullOpusSideCommentNav").css("display","none");

        // when active para change
        var indexOfPara=$(".sideCommentView").index($(this));
        activeParaChange(indexOfPara);

        return false;
    })

    // edit the side comment of this para
    $(".sideCommentEdit").click(function(){
        // when active para change
        var indexOfPara=$(".sideCommentEdit").index($(this));
        editingParaNum=indexOfPara;
        activeParaChange(indexOfPara);

        // set position of editing area under the para
        var buttomOfActivePara=editableOpusChild.eq(indexOfPara).offset().top+editableOpusChild.eq(indexOfPara).height()-60;
        $(".sideCommentEditBox").css({"top":buttomOfActivePara+"px"});
        $(".sideCommentEditBox").fadeIn(100);

        // auto focus on edit area
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
        editingParaNum=-1;
        return false;
    });

    // send editting side comment
    $("#sideCommentEditSend").click(function(){
        // content:sideCommentCon,paraNum:editingParaNum
        var content=$("#sideCommentEditData").val();
        var url = location.pathname + '/comment/side';
        $.post(url,
        {
            'content': content,
            'paragraph_id': editingParaNum, // TODO: replace this
        },
        function(data) {
            // TODO: if 'failed'
            var sideComment=eval("("+data+")");
            paraId=sideComment.paragraph_id;
            // console.log(sideComment.paragraph_id,sideComment.uid,sideComment.penname,sideComment.content);
            var sideCommentShowBox='<li class="opusSideCommentList opusSideCommentList'+sideComment.paragraph_id+'" style="background:pink;width:253px">'
                           +   '<a href="/u/'+sideComment.uid+'" class="opusSideCommentListUserName">'+sideComment.penname+'</a>'
                           +   '<div class="opusSideCommentContent">'
                           +        sideComment.content
                           +   '</div>'
                           +'</li>';
            var addListNav=$("#sideCommentNode"+sideComment.paragraph_id).children(".opusSideCommentNav");
            addListNav.after(sideCommentShowBox);
            if (addListNav.hasClass("nullOpusSideCommentNav")) {
                var preNav='<li class="opusSideCommentList opusSideCommentList'+paraId+' opusSideCommentNav" style="width:253px">'
                        +'第'+paraId+'段评论('+'<span class="numOfParaComent">'+($("#sideCommentNode"+paraId).children().size()-1)+'</span>'+')'
                        +'</li>';
                addListNav.after(preNav);
                addListNav.remove();
            };
            $("#sideCommentEditData").val("");
            $(".sideCommentEditBox").fadeOut();
        });
        return false;
    });

    // send buttom comment
    // TODO: It's 'bottom' not 'buttom'
    $("#buttomCommentSend").click(function(){
        var content=$("#opusCommentData").val();
        var url = location.pathname + '/comment/bottom';
        // console.log(deleteBrPara(content));
        $.post(url,
        {
            'content': content,
            'page_id': 0, // TODO: replace this
        },
        function(data, status) {
            // TODO: if 'failed'
            var buttomCommentShowBox = data;
            if ($(".opusCommentList").size()==0) {
                $(".buttomComment").append(buttomCommentShowBox);

            }else{
                $(".opusCommentList").last().removeClass("noBorderButtom");
                $(".opusCommentList").last().after(buttomCommentShowBox);
            };
            $(".opusCommentList").last().addClass("noBorderButtom");
            $(window.frames["ueditor_0"].document).find("body.view").html("");
        });
        return false;
    });

});

function init(){
    var totalNumOfPara=editableOpusChild.size();
    // initial sideCommentNode
    for (var i=0;i<totalNumOfPara;i++){
        var sideCommentNode='<div class="sideCommentNode" id="sideCommentNode'+i+'">';
        $(".opusSideComment").append(sideCommentNode);
    };

    // initial para function bution
    for (var i =0; i<editableOpusChild.size(); i++) {
        var viewCommentButton='<a href="#" class="sideCommentView">查看评论</a><a href="#" class="sideCommentEdit">编辑评论</a>';
        editableOpusChild.eq(i).append(viewCommentButton);
    };

    // load sidecomment in sideCommentNode
    var url = location.pathname + '/comment/side';
    $.getJSON(url, function(data) {
        for(var i=0;i<totalNumOfPara;i++){
            for (var j=0; j<data.length; j++) {
                var comment = data[j];
                var paragraph_id = comment.split('\n')[0].match(/\d+/g)[0];
                if (paragraph_id != i)
                    continue;
                $("#sideCommentNode"+i).prepend(comment);
            }
        };

        // if sideCommentNode has no comment,add a appNull,if not,add a Nav
        for(var i=0;i<totalNumOfPara;i++){
            var preNav='<li class="opusSideCommentList opusSideCommentList'+i+' opusSideCommentNav" >'
                        +'第'+i+'段评论('+'<span class="numOfParaComent">'+$("#sideCommentNode"+i).children().size()+'</span>'+')'
                        +'</li>';
            var preNull='<li class="opusSideCommentList opusSideCommentList'+i+' opusSideCommentNav nullOpusSideCommentNav" >'
                        +'这个段落目前还没有评论，你可以通过“编辑评论”开始创建'
                        +'</li>';

            var thisSideCommentNode=$("#sideCommentNode"+i);
            if (thisSideCommentNode.children().size()!=0) {
                thisSideCommentNode.prepend(preNav);
            }else{
                thisSideCommentNode.prepend(preNull);
            };
        };
    });
    // other set
    editableOpusChild.addClass("opusMainChildren");
    $(".opusCommentList").last().addClass("noBorderButtom");
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
       return $(window).height()-(topPartHeight()+buttomPartHeight())-10;
    };
    return $(window).height()-(topPartHeight()+buttomPartHeight())+30;
}

function activeParaChange(indexOfPara){
    $(".activeOpusSideCommentList").removeClass("activeOpusSideCommentList");
    $(".activeOpusSideCommentNav").removeClass("activeOpusSideCommentNav");
    $(".activeOpusPara").removeClass("activeOpusPara");
    editableOpusChild.eq(indexOfPara).addClass("activeOpusPara");
    if ($(".opusSideCommentList"+indexOfPara).css("display")!="none") {
        var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
        $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});
        $("#sideCommentNode"+indexOfPara).children().addClass("activeOpusSideCommentList");
        $(".opusSideCommentList"+indexOfPara).eq(0).removeClass("activeOpusSideCommentList").addClass("activeOpusSideCommentNav");
    }else{
        $(".opusSideCommentList"+indexOfPara).eq(0).fadeIn(500,function(){
            var offsetHeightOfSideCommnetChild=$(".opusSideCommentList"+indexOfPara).eq(0).position().top + $(".opusSideComment").scrollTop();
            $(".opusSideComment").animate({scrollTop:+offsetHeightOfSideCommnetChild});
        });
    };
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
    $('html,body').animate({scrollTop:top},10);
    $('#buttomCommentSend').css({"margin-right":"-17px"});
}

function foldSideComment(){
    $("#expandSideComment").text("展开侧评");
    $(".opusSideCommentWrap").fadeOut(50);
    $(".activeOpusPara").removeClass("activeOpusPara");
    editableOpusChild.removeClass("activeOpusPara");
    editableOpusChild.css({"color":"rgb(68,68,68)","opacity":"1.0"});
    var top=$(window).scrollTop();
    $(".readMain").removeClass("floatReadMain");
    $(".read").css({"width":"1060px"});
    $('html,body').animate({scrollTop:top},500,function(){
        $(".activeOpusPara").removeClass("activeOpusPara");
    });
    $(".sideCommentView,.sideCommentEdit").hide();
    $(".opusSideCommentWrap").addClass("noTransition");
    $("#buttomCommentSend").css({"margin-right":"0"});
}

