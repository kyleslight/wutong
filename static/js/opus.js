var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var topOfSight=150;
var editingParaNum=-1;
var is_image_view=false;
var editableOpusChild=$(".opusMain").children("div,p,table,blockquote");
var sideCommentState=false;
var opusScore=0;
// 评分, 收藏
var interactInfo = null;

$(document).ready(function(){

    editableOpusChild=$(".opusMain").children("div,p,table,blockquote");
    // initializing the opus and side commnet
    init();

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
    });

    editableOpusChild.click(function(){
        if ($(".opusSideCommentWrap").css("display")=="none"){
            return false;
        };
        $(".nullOpusSideCommentNav").css("display","none");

        // when active para change
        var indexOfPara=editableOpusChild.index($(this));
        activeParaChange(indexOfPara);
        // toLeftPara(indexOfPara);

        return false;
    });

    // edit the side comment of this para
    editableOpusChild.dblclick(function(){
        if ($(".opusSideCommentWrap").css("display")=="none") {
            return false;
        }
        var indexOfPara=editableOpusChild.index($(this));
        sideCommentShow(indexOfPara);
    });
    $(".sideCommentEdit").click(function(){
        var indexOfPara=$(".sideCommentEdit").index($(this));
        sideCommentShow(indexOfPara);
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
        sendSideComment();
        return false;
    });
    // quick side comment send
    $("#sideCommentEditData").bind({
        focus:function(){sideCommentState=true;},
        blur:function(){sideCommentState=false;}
    });
    $(window).keyup(function(e) {
        var keyCode = e.keyCode;
        if (keyCode==13&&e.ctrlKey&&sideCommentState) {
            sendSideComment();
        };
        return false;
    });

    // collect opus
    $("#collectOpus").click(function(){
        var collectionUrl=location.pathname+"/interact?collect";
        $.post(collectionUrl, function(data){
            var err = getError(data);
            if (err) {
                perror(err);
                return;
            }
            var msg;
            if (interactInfo.is_collected) {
                msg = "取消收藏成功";
            } else {
                msg = "收藏成功";
            }
            showError(msg, 2000);
            $("#collectOpus").fadeOut();
            return false;
        });
        return false;
    });

    function paintScoreBar(indexOfHoverBar) {
        $(".scoreBar").css({"background":"white"});
        for(var i=0;i<indexOfHoverBar;i++){
            var opacityOfBarBefore=i*0.08+0.2;
            var backgroundColor='rgba(102,136,0,'+opacityOfBarBefore+')';
            $(".scoreBar").eq(i).css({"background":backgroundColor});
        };
        $("#score").text(indexOfHoverBar);
        switch(indexOfHoverBar){
            case 1:$("#scoreDescription").text('/非常差，糟糕至极');break;
            case 2:$("#scoreDescription").text('/非常差，但可以忍受');break;
            case 3:$("#scoreDescription").text('/较差，将就着看');break;
            case 4:$("#scoreDescription").text('/较差，总体上过得去');break;
            case 5:$("#scoreDescription").text('/还行，有潜力');break;
            case 6:$("#scoreDescription").text('/还行，有些地方不错');break;
            case 7:$("#scoreDescription").text('/很好，推荐');break;
            case 8:$("#scoreDescription").text('/很好，力荐');break;
            case 9:$("#scoreDescription").text('/非常好，经典之作');break;
            case 10:$("#scoreDescription").text('/非常好，登峰造及');break;
            default:break;
        };
    }

    $("#scoreOpus").click(function(){
        $(".scoreBoard").slideDown();
        opusScore = parseInt(interactInfo.score);
        if (opusScore) {
            paintScoreBar(opusScore);
            $("#score").text(opusScore);
        }
        return false;
    });

    $(".scoreBar").hover(function(){
        var indexOfHoverBar=$(".scoreBar").index($(this))+1;
        paintScoreBar(indexOfHoverBar);
    });

    $(".scoreBar").click(function(){
        opusScore=$(".scoreBar").index($(this))+1;
        $("#score").text(opusScore);
        return false;
    });
    $(".scoreBarWrap").mouseleave(function(){
        if (opusScore!=0) {return false;};
        $(".scoreBar").css({"background":"white"});
        $("#score").text("未评价");
        $("#scoreDescription").text("");
    });
    $("#sendScore").click(function(){
        if (opusScore==0) {
            showError("请先进行评分再提交",2000);
            return false;
        };
        var scoreUrl=location.pathname+"/interact";
        var score = parseInt($("#score").text());
        $.post(scoreUrl,{
            'score': score
        },function(data){
            if (data) {
                $("#scoreBoardBeforeBack").click();
            } else {
                interactInfo.score = score;
                showError("评分成功",2000);
                $("#scoreBoardBeforeBack").click();
                return false;
            }
        });
    });
    $("#scoreBoardBeforeBack").click(function(){
        $(".scoreBoard").slideUp();
        opusScore=0;
        $(".scoreBar").css({"background":"white"});
        $("#score").text("未评价");
        $("#scoreDescription").text("");
        return false;
    });

    $("#buttomCommentSend").click(function(){
        if (!checkLogin) {
            showError("要发送底评请先登录",2000);
            return false;
        };
        if (BCeditor.getContentLength()==0) {
            showError("底评内容不能为空",2000);
            return false;
        };
        if (BCeditor.getContentLength()>10000) {
            showError("底评发送字数超过10000字数上限",3000);
            return false;
        };
        var content=$("#opusCommentData").val();

        var url = location.pathname + '/comment?create';
        // TODO: 被回复的comment_id
        var reply_id = null;
        $.post(url, {
            'content': content,
            'reply_id': reply_id,
            'type': 'bottom',
        }, function(data) {
            var err = getError(data);
            if (err) {
                console.log(err);
                return;
            }
            data = JSON.parse(data);
            if ($(".opusCommentList").size() != 0) {
                $(".opusCommentList").last().removeClass("noBorderButtom");
            }
            renderTemplateAfter('#bottom-comment-template', data)
            $(".buttomCommentCon").children().last().addClass("noBorderButtom");
            BCeditor.setContent("");
        });
        return false;
    });

    // init ueditor
    BCeditor.ready(function(){
        initUeditor(2);
    });

});

function init(){
    var totalNumOfPara=editableOpusChild.size();
    // 延迟加载
    // 获取 评分, 收藏 等信息
    $.getJSON(location.pathname + '/interact', function(data) {
        $.getJSON(location.pathname + '/comment?side', function(data) {
            $.getJSON(location.pathname + '/comment?bottom', function(data) {
                var err = getError(data);
                if (err) {
                    console.log(err);
                    return;
                }

                for (var i = 0; i < data.length; i++)
                    renderTemplateAfter('#bottom-comment-template', data[i])
                $(".buttomCommentCon").children().last().addClass("noBorderButtom");
            });

            var err = getError(data);
            if (err) {
                console.log(err);
                return;
            }

            for(var i=0;i<totalNumOfPara;i++){
                for (var j=0; j<data.length; j++) {
                    // TODO
                    // var comment = data[j];
                    var comment = data[j].content;
                    // var paragraph_id = comment.split('\n')[0].match(/\d+/g)[0];
                    var paragraph_id = data[j].paragraph_id;
                    if (paragraph_id != i)
                        continue;
                    $("#sideCommentNode"+i).prepend(comment);
                }
            };

            // if sideCommentNode has no comment,add a appNull,if not,add a Nav
            for(var i=0;i<totalNumOfPara;i++){
                var preNav='<li class="opusSideCommentList opusSideCommentList'+i+' opusSideCommentNav" onclick="toLeftPara('+i+')">'
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

        if (getError(data)) {
            perror();
            return;
        };
        interactInfo = data;
    });

    // initial sideCommentNode
    for (var i=0;i<totalNumOfPara;i++){
        var sideCommentNode='<div class="sideCommentNode" id="sideCommentNode'+i+'">';
        $(".opusSideComment").append(sideCommentNode);
    };

    // initial para function bution
    for (var i =0; i<editableOpusChild.size(); i++) {
        var viewCommentButton=''
        // +'<a href="#" class="sideCommentView">查看评论</a><br>'
        +'<a href="#" class="sideCommentEdit" title="编辑侧评"><img /></a>';
        editableOpusChild.eq(i).prepend(viewCommentButton);
    };
    // other set
    $(".opusCommentList").last().addClass("noBorderButtom");
    // console.log($(".opusMain").children().eq(0).attr("class"));
    if ($(".opusMain").children().eq(0).hasClass("imageUpload")) {
        is_image_view=true;
        // $(".readMain").css({"background":"black","border":"0"});
        $(".opusMain").children().css({"background":"none"});
        $(".opusMainTitle").css({"color":"black"});
        $(".readMain").css({"box-shadow":"none"});
        $(".opusSuffixes a").css({"color":"rgba(102,0,0,0.64)"});
        $(".opusComment").css({"border-top":"1px solid rgba(102,0,0,0.64)"});
        $("#edui1").css({"border":"1px solid lightblue"});
    };
    var reference=$(".opusReferenceCon").text();
    $(".opusReferenceCon").empty().append(reference);

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

function sideCommentShow(indexOfPara){
    if (!checkLogin) {
        showError("要发送侧评请先登录",2000);
        return false;
    };
    // when active para change
    editingParaNum=indexOfPara;
    activeParaChange(indexOfPara);

    // set position of editing area under the para
    var buttomOfActivePara=editableOpusChild.eq(indexOfPara).offset().top+editableOpusChild.eq(indexOfPara).height()-60;
    if (is_image_view) {
        $(".sideCommentEditBox").css({"top":(buttomOfActivePara+30)+"px"});
    }else{
        $(".sideCommentEditBox").css({"top":buttomOfActivePara+"px"});
    };
    $(".sideCommentEditBox").fadeIn(100);

    // auto focus on edit area
    var sideCommentEditFocus = document.getElementById("sideCommentEditData");
    sideCommentEditFocus.focus();

    return false;
}

function sendSideComment(){
    var content=$("#sideCommentEditData").val();
    if (content.length==0) {
        showError("侧评内容不能为空",2000);
        return false;
    };
    if (content.length>280) {
        showError("侧评发送字数超过280字数上限",2000);
        return false;
    };

    content=content.replace(/</g,"&lt").replace(/>/g,"&gt");
    content=content.httpHtml();
    content=content.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");

    var url = location.pathname + '/comment';
    $.post(url, {
        'content': content,
        'paragraph_id': editingParaNum, // TODO: replace this
        'type': 'side'
    }, function(data) {
        var err = getError(data);
        if (err) {
            showError("发送失败",2000);
            return false;
        };
        data = JSON.parse(data);
        data.content = data.content.replace(/&lt;br \/&gt;/g,"<br>")
                                   .replace(/&lt;\/a&gt;/g,"</a>")
                                   .replace(/&gt;/g,">")
                                   .replace(/&lt;a/g,"<a")
                                   .replace(/&quot;/g,"'");
        // TODO
        var html = renderTemplateAfter('#side-comment-template', data);
        console.log(html);
        var addListNav=$("#sideCommentNode"+data.paragraph_id).children(".opusSideCommentNav");
        addListNav.after(data);
        $(".opusSideCommentList"+data.paragraph_id).eq(1).css({"background":"pink","width":"268px"});
        if (addListNav.hasClass("nullOpusSideCommentNav")) {
            var preNav='<li class="opusSideCommentList opusSideCommentList'+editingParaNum+' opusSideCommentNav" style="width:253px" onclick="toLeftPara('+editingParaNum+')">'
                    +'第'+editingParaNum+'段评论('+'<span class="numOfParaComent">'+($("#sideCommentNode"+editingParaNum).children().size()-1)+'</span>'+')'
                    +'</li>';
            addListNav.after(preNav);
            addListNav.remove();
        };
        $(".opusSideCommentList"+editingParaNum).eq(1).css({"background":"pink","width":"253px"});
        $(".opusSideCommentList"+editingParaNum).eq(0).css("width","253px");
        $("#sideCommentEditData").val("");
        $(".sideCommentEditBox").fadeOut();
    });
    return false;
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
    editableOpusChild=$(".opusMain").children("div,p,table,blockquote");
    editableOpusChild.addClass("opusMainChildren").addClass("pointerPara");
}

function foldSideComment(){
    $("#expandSideComment").text("侧评");
    $(".opusSideCommentWrap").fadeOut(50);
    $(".activeOpusPara").removeClass("activeOpusPara");
    editableOpusChild.removeClass("activeOpusPara").removeClass("pointerPara");
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

function toLeftPara(paraID){
    var paraOffTop=editableOpusChild.eq((paraID)).offset().top-170;
    $('html,body').animate({scrollTop:paraOffTop+"px"},function(){
        activeParaChange(paraID);
    });
}

