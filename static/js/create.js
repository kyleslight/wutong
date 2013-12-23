var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var opusShowTime=1000;

$(document).ready(function(){

    $("#IsPreviewBeforePublic").change(function(){
        if (!$(this).prop('checked')) {
            $("#opusPreViewButton").hide();
            $("#opusPublicSubmitButton,#opusPrivateSubmitButton").show();
        }else{
            $("#opusPreViewButton").show();
            $("#opusPublicSubmitButton,#opusPrivateSubmitButton").hide();
        };
    });

    $("#opusPreViewButton").click(function(){
        $("#textdata,#opusPreViewButton,#previewBeforePublic").fadeOut();
        var mainText=$("#textArea").val();
        // console.log($("#title").val(),$("#foreword").val(),$("#reference").val(),($("#articleFirstClass").val()+$("#otherTags").val()),$("#suit").val(),$("#cooperation").val(),$("#puclicPush").prop('checked'));
        var temTextData={
            title:$("#title").val(),
            foreword:$("#foreword").val(),
            mainText:$("#textArea").val(),
            reference:$("#reference").val(),
            tags:[  $("#articleFirstClass").val(),
                    $("#otherTags").val()],
            suit:$("#suit").val(),
            cooperation:$("#cooperation").val(),
            is_pushed:$("#puclicPush").prop('checked'),
            type:$(".activeOpusType").text()
        }
        // console.log(temTextData);
        var temTime=new Date();
        var temtText='<div class="opusBasicInfo">'
                    +    '<div class="firstLine">'
                    +        '<div class="opusTime">'+temTime.getFullYear()+' '+(temTime.getMonth()+1)+' '+temTime.getDate()+'</div>'
                    +        '<span class="opusAuthor">by <a href="#">'+userInfo.penname+'</a></span>'
                    +    '</div>'
                    +    '<div class="opusTitle">'
                    +        '<div class="opusMainTitle">'+temTextData.title+'</div>'
                    +    '</div>'
                    +    '<div class="opusDescription">'
                    +        temTextData.foreword
                    +    '</div>'
                    +    '<div class="opusAppositeness">适合：<span calss="opusAppositenessContent">'+temTextData.suit+'</span></div>'
                    +'</div>'

                    +'<div class="opusMain">'
                    +    temTextData.mainText
                    +'</div>'
                    +'<div class="opusSuffixes">'
                    +    '<div class="opusReference">参考来源：<a href="#">'+temTextData.reference+'</a>'
                    +    '</div>'
                    +    '<div class="opusTag">Tags： '+temTextData.tags
                    +    '</div>'
                    +'</div>'
        $("#temTextData").prepend(temtText);
        $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").fadeIn();
    });
    $("#opusPreViewBack").click(function(){
        $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").fadeOut();
        $("#textdata,#opusPreViewButton,#previewBeforePublic").fadeIn();
    })

    $("#opusPublicSubmitButton,#opusPrivateSubmitButton").click(function(){
        
        // 发送需要的数据
        // var opusAttachedData={
            // opusType : $(".activeOpusType").text(),                      作品类型，包括“文章”，“片段”，“摄影”，“绘画”，“音乐”，“视频”，“项目”
            // opusPublicity : isPublic($(this).attr("id")),                作品公开性，返回true，false
            // opusIsPushed : $("#puclicPush").prop('checked')              作品是否推送，返回true，false
        // };
        // make null para not a child of opus
        var mainText=$("#textArea").val();
        mainText=deleteBrPara(mainText);
        $("#textArea").val(mainText);
        var theForm=document.getElementById("textdata");
        theForm.submit();
    });

    $(".inputTip a").click(function(){
        var indexofa=$(".inputTip a").index($(this))+1;
        if ($("#formlisttip"+indexofa).css("display")=="none") {
            $("#formlisttip"+indexofa).slideDown(1000);
            $(this).parent().parent().addClass("offborformlist").removeClass("formlist");
        }
        else{
            $("#formlisttip"+indexofa).slideUp(1000);
            $(this).parent().parent().addClass("formlist").removeClass("offborformlist");
        }
        return false;
    });

    $(window).scroll(function(){
        var top=$(window).scrollTop();
        if(top>200){
            var realHeight=(top+(window.screen.availHeight)/2)+'px';
            $('#return_top').removeClass('none');
            $('#return_top').stop();
            $('#return_top').animate({top:realHeight},500);
        }
        else{
            $('#return_top').addClass('none');
        }
        return false;
    });
    $(".opusType").click(function(){
        $(".activeOpusType").removeClass("activeOpusType");
        $(this).addClass("activeOpusType");
    });
    $("#opusTypeAreaSwitch").click(function(){
        if ($("#opusTypeOption").css("display")=="none") {
            $("#opusTypeOption").slideDown();
            $(this).text("隐藏作品类型")
        }else{
            $("#opusTypeOption").slideUp();
            $(this).text("展开作品类型");
        }
    });

    $("#opusExpandBotton").click(function(){
        if ($(".expandOption").css("display")=="none") {
            $(".expandOption").show();
            $(this).text("隐藏作品扩展项");
        }else{
            $(".expandOption").hide();
            $(this).text("显示作品扩展项");
        };
        return false;
    });



});

function isPublic(bottonId){
    if (bottonId=="opusPublicSubmitButton") {
        return true;
    }else{return false;};
    return false;
}

function deleteBrPara(string){
    var deletaBrReg=/<p>(<br\/>)+<\/p>/g;
    var deleteSpaceReg=/<p>(&nbsp;| &nbsp;)+<\/p>/g;
    string=string.replace(deletaBrReg,"<br/>");
    string=string.replace(deleteSpaceReg,"<br/>");
    return string;
}



