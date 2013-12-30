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
        $("#temTextData").html("");
        $("#textdata,#opusPreViewButton,#previewBeforePublic").hide();
        var mainText=$("#textArea").val();
        // console.log($("#title").val(),$("#foreword").val(),$("#reference").val(),($("#articleFirstClass").val()+$("#otherTags").val()),$("#suit").val(),$("#cooperation").val(),$("#puclicPush").prop('checked'));
        var temTextData={
            title:$("#title").val(),
            foreword:$("#foreword").val(),
            mainText:$("#textArea").val(),
            reference:$("#reference").val(),
            tags:[  $(".activeFirstClass").val()+" "+
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
        $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").show();
    });
    $("#opusPreViewBack").click(function(){
        $("#temTextData,#opusPreViewBack,#opusPublicSubmitButton,#opusPrivateSubmitButton").hide();
        $("#textdata,#opusPreViewButton,#previewBeforePublic").show();
    })

    $("#opusPublicSubmitButton,#opusPrivateSubmitButton").click(function(){
        var mainText=$("#textArea").val();
        mainText=deleteBrPara(mainText);
        $("#textArea").val(mainText);
        var transTags=$(".activeFirstClass").val()+";"+$("#otherTags").val();
        $("#otherTags").val(transTags);
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
        switch($(this).text()){
            case "文章":
                changeOpusItem(1,1,1,0,0);break;
            case "片段":
                changeOpusItem(0,0,1,0,1);break;
            case "摄影":
                changeOpusItem(1,1,0,1,2);break;
            case "绘画":
                changeOpusItem(1,0,0,1,3);break;
            case "项目":
                changeOpusItem(1,1,1,2,4);break;
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
    });
    $(".deletePreImage").click(function(){
        console.log("a");
        var preImageIndex = $(".deletePreImage").index($(this));
        $(".preImageUpload").eq(preImageIndex).remove();
        return false;
    });

    // init ueditor
    editor.ready(function(){
        initUeditor(0);
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

// title:0 1 0:optional 1:required
// foreword:0 1 0:null 1:optional
// mainText:0 1 0:show 1:none
// resource:0 1 2 0:null 1:image 2:file

function changeOpusItem(title,foreword,mainText,resource,tags){
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
}



