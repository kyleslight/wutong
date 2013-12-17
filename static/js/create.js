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

    $("#opusPublicSubmitButton,#opusPrivateSubmitButton").click(function(){
        
        // 发送需要的数据
        // var opusAttachedData={
            // opusType : $(".activeOpusType").text(),                      作品类型，包括“文章”，“片段”，“摄影”，“绘画”，“音乐”，“视频”，“项目”
            // opusPublicity : isPublic($(this).attr("id")),                作品公开性，返回true，false
            // opusIsPushed : $("#puclicPush").prop('checked')              作品是否推送，返回true，false
        // };
        // var theForm=document.getElementById("textdata");
        // theForm.submit();
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



