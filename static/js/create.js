var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var opusShowTime=1000;

$(document).ready(function(){

    initCreate();

    $("#IsPreviewBeforePublic").change(function(){
        if (!$(this).prop('checked')) {
            $("#opusPreViewButton").hide();
            $("#opusPublicSubmitButton,#opusPrivateSubmitButton").show();
        }else{
            $("#opusPreViewButton").show();
            $("#opusPublicSubmitButton,#opusPrivateSubmitButton").hide();
        };
    });

    $(window).scroll(function(){
        var top=$(window).scrollTop();
        var editorTop=editor.container.offsetTop;
        var editorHeight=editor.container.offsetHeight;
        if (top>editorTop&&top<(editorTop+editorHeight)) {
            $("#edui1_toolbarbox").addClass("floatEditorBtn");
        }else{
            $("#edui1_toolbarbox").removeClass("floatEditorBtn");
        };
    });

    $("#opusPreViewButton").click(function(){
        // check form
        if($("#title").val().length==0){
            showError("请填写标题",2000);
            return false;
        };
        if($("#title").val().length>25){
            showError("标题请保持在25字以内",2000);
            return false;
        };
        if($("#foreword").val().length>200) {
            showError("引言请保持在200字以内",2000)
        };

        var preTag=$("#otherTags").val().split(";");
        for(var i=0;i<preTag.length;i++){
            if (lessIllegalCharacter.test(preTag[i])) {
                showError("Tag包含非法字符",2000);
                return false;  
            };
        };

        $("#imageUploadContainer").html("");
        if ($(".activeOpusType").text()=="摄影"||$(".activeOpusType").text()=="绘画") {
            for(var i=0;i<$(".preImageUpload").size();i++){
                var imgUrl=$(".preImageUpload").children("img").eq(i).attr("src");
                var imgIntro=$(".preImageUpload").children(".preImageIntro").eq(i).val();
                var appImage='<div class="imageUpload" style="background:rgba(0,0,0,0.8);padding-top:20px;padding-bottom:20px;">'
                                 +  '<img src="'+imgUrl+'" />'
                                 +  '<div class="imageIntro"><p>'+imgIntro+'</p></div>'
                                 +'</div>';
                $("#imageUploadContainer").append(appImage);
            }
            var mainText=$("#imageUploadContainer").html();
        }else{
            var mainText=$("#textArea").val();
        };

        var mainTextLength=editor.getContentLength();
        if (mainTextLength>30000) {
            showError("作品正文长度超过30000的字数上限<br>请合理分割您的作品，分次上传",4000);
            return false;
        };

        if (mainText=="") {
            showError("请添加正文/照片",2000)
            return false;
        };

        $("#temTextData").html("");

        var temTextData={
            title:$("#title").val(),
            foreword:$("#foreword").val(),
            mainText:mainText,
            reference:preReference($("#reference").val()),
            tags:[  $(".activeFirstClass").val()+" "+
                    $("#otherTags").val()],
            suit:$("#outterSuit").val(),
            cooperation:$("#cooperation").val(),
            is_pushed:$("#puclicPush").prop('checked'),
            type:$(".activeOpusType").text()
        }
        // console.log($("#title").val(),$("#foreword").val(),$("#reference").val(),($("#articleFirstClass").val()+$("#otherTags").val()),$("#suit").val(),$("#cooperation").val(),$("#puclicPush").prop('checked'));
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
                    +    '<div class="opusReference">参考来源：'+temTextData.reference
                    +    '</div>'
                    +    '<div class="opusTag">Tags： '+temTextData.tags
                    +    '</div>'
                    +'</div>'
        $("#temTextData").prepend(temtText);

        if ($(".opusMain").children().size()>700) {
            showError("请保持您的正文在700段以内",4000);
            $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").hide();
            $("#textdata,#opusPreViewButton,#previewBeforePublic").show();
            return false;
        };

        if (temTextData.suit=="") {
            $(".opusAppositeness").hide();
        };
        if (temTextData.reference=="") {
            $(".opusReference").hide();
        };
        $("#textdata,#opusPreViewButton,#previewBeforePublic").hide();
        $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").show();
    });
    $("#opusPreViewBack").click(function(){
        $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").hide();
        $("#textdata,#opusPreViewButton,#previewBeforePublic").show();
    })

    $("#opusPublicSubmitButton,#opusPrivateSubmitButton").click(function(){
        if ($(".activeOpusType").text()=="摄影"||$(".activeOpusType").text()=="绘画") {
            $("#imageUploadContainer").html("");
            for(var i=0;i<$(".preImageUpload").size();i++){
                var imgUrl=$(".preImageUpload").children("img").eq(i).attr("src");
                var imgIntro=$(".preImageUpload").children(".preImageIntro").eq(i).val();
                var appImage='<div class="imageUpload" style="background:rgba(0,0,0,0.8);padding-top:20px;padding-bottom:20px;">'
                                 +  '<img src="'+imgUrl+'" />'
                                 +  '<div class="imageIntro"><p>'+imgIntro+'</p></div>'
                                 +'</div>';
                $("#imageUploadContainer").append(appImage);
            }
            var mainText=$("#imageUploadContainer").html();
        }else{
            var mainText=$("#textArea").val();
        };
        mainText=deleteBrPara(mainText);
        $("#textArea").val(mainText);
        var transTags=$(".activeFirstClass").val()+";"+$("#otherTags").val();
        $("#opusType").val($(".activeOpusType").text());
        $("#opusTag").val(transTags);
        $("#opusSuit").val($("#outterSuit").val());
        $("#opusCooperation").val($("#outterCooperation").val());
        var referenceCon=preReference($("#reference").val());       
        $("#reference").val(referenceCon);

        var theForm=document.getElementById("textdata");
        console.log(theForm);
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
    $(".opusType").click(function(){
        if ($(this).hasClass("activeOpusType")) {
            return;
        };
        activeItemChange($(this),"activeOpusType");
        // title:0 1 0:optional 1:required
        // foreword:0 1 0:null 1:optional
        // mainText:0 1 0:optional 1:required
        // resource:0 1 2 0:null 1:image 2:file
        // tags:0 1 2 3 4 0:article 1:fragment 2:photograph 3:drawing 4:project
        // subtleChange:0 1 0:foreword bottom border hide 1:foreword bottom border show
        switch($(this).text()){
            case "文章":
                changeOpusItem(1,1,1,0,0,1);break;
            case "片段":
                changeOpusItem(0,0,1,0,1,1);break;
            case "摄影":
                changeOpusItem(1,1,0,1,2,0);break;
            case "绘画":
                changeOpusItem(1,1,0,1,3,0);break;
            case "项目":
                changeOpusItem(1,1,1,2,4,1);break;
        };
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
    $(".addImage").click(function(){
        insertImage(1);
        return false;
    });

    // init ueditor
    editor.ready(function(){
        initUeditor(0);
    });

});

function initCreate(){
    $.get("/u/info",function(data){
        if (!data) {
            showError("创作作品前请先登录",2000);
        };
    });
}

function isPublic(bottonId){
    if (bottonId=="opusPublicSubmitButton") {
        return true;
    }else{return false;};
    return false;
}

function deleteBrPara(string){
    // var deletaBrReg=/<p>(<br\/>)+<\/p>/g;
    var deleteSpaceReg=/<p>(&nbsp;| &nbsp;|<br\/>)+<\/p>/g;
    // string=string.replace(deletaBrReg,"<br/>");
    string=string.replace(deleteSpaceReg,"<br/>");
    return string;
}

// title:0 1 0:optional 1:required
// foreword:0 1 0:null 1:optional
// mainText:0 1 0:show 1:none
// resource:0 1 2 0:null 1:image 2:file

function changeOpusItem(title,foreword,mainText,resource,tags,subtleChange){
    // title
    // if (title) $("#title").attr("placeholder","填写标题"); else  $("#title").attr("placeholder","填写标题（可选）");
    // foreword
    if (foreword) $("#forewordForm").show(); else $("#forewordForm").hide();
    // mainText
    if (mainText) $("#mainTextForm").show(); else $("#mainTextForm").hide();
    // resource
    switch(resource){
        case 0:$("#resourceForm").hide();$("#imageresourceForm").hide();break;
        case 1:$("#resourceForm").hide();$("#imageresourceForm").show();break;
        case 2:$("#resourceForm").show();$("#imageresourceForm").hide();break;
        default:break;
    };
    // tags
    $(".activeFirstClass").removeClass("activeFirstClass");
    $(".firstClass").eq(tags).addClass("activeFirstClass");
    // subtleChange
    if (subtleChange==0){
        $("#forewordForm").addClass("forewordFormNoBottomLine");
    }else{
        $("#forewordForm").removeClass("forewordFormNoBottomLine");
    }
}

function preReference(reference){
    reference=reference.replace(/</g,"&lt").replace(/>/g,"&gt");
    reference=reference.httpHtml();
    reference=reference.toString().replace(/(\r)*\n/g,"<br />").replace(/\s/g," ");
    return reference;
}

String.prototype.httpHtml = function() {
    var reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-|:)+)/g;
    return this.replace(reg, '<a href="$1$2" target="_blank">$1$2</a>');
}



