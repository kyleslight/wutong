var userAgeState=false;
var dateRe=/\d{4}-\d{2}-\d{2}/im;
var dateLessRe=/\d{4}-\d{1}-\d{1}/im;

$(document).ready(function(){

    $(".opusCommentButton").click(function(){
        $(".activeOpusCommentButton").removeClass("activeOpusCommentButton");
        $(".activeOpusCommentPart").removeClass("activeOpusCommentPart");
        var indexOfOpusCommentPart=$(".opusCommentButton").index($(this));
        $(".opusCommentButton").eq(indexOfOpusCommentPart).addClass("activeOpusCommentButton");
        $(".opusCommentPart").eq(indexOfOpusCommentPart).addClass("activeOpusCommentPart");
        return false;
    });

    $("#edittingAge").bind({
        focus:function(){userAgeState=true;},
        blur:function(){userAgeState=false;}
    });

    // 头像上传
    $(".userImage").click(function(){
        // 更改头像需将图像上传修复了才能做
    });

    // 关注
    $("#follow").click(function(){
        if (!checkLogin) {
            showError("请先登录",2000);
            return false;
        };
    });
    // 会话
    $("#chat").click(function(){
        if (!checkLogin) {
            showError("请先登录",2000);
            return false;
        };
        // 申请会话后后台需向被申请者发出一条消息，并给出两条选项“是”或“否”
        // 若被申请者接受，则创建一个名为 被申请者名-申请者名+"的会话” 的私人小组
        // 该小组不接受外部申请加入，没有公告等小组信息项
    });

    // edit user info
    $("#userInfoEdit").click(function(){
        $(".editableArea").slideUp();
        $(".edittingArea").slideDown();
        return false;
    });
    $("#userEditedBack").click(function(){
        $(".editableArea").slideDown();
        $(".edittingArea").slideUp();
        return false;
    });
    $("#userEditedSubmit").click(function(){
        var userEdittingInfo={};
        var motto = $("#edittingMotto").val(),
            intro = $("#edittingIntro").val(),
            sex   = checkSex(),
            birthday = $("#edittingAge").val(),
            address = $("#edittingCity").val();

        if (motto.length>50) {
            showError("请保持签名在50字以内",2000);
            return false;
        }else if (motto.length!=0) {
            userEdittingInfo.motto = motto;
        };

        if (intro.length>50) {
            showError("请保持个人简介在50字以内",2000);
            return false;
        }else if (intro.length!=0) {
            userEdittingInfo.intro = intro;
        };

        if (sex!="") {
            userEdittingInfo.sex = sex;
        };

        if (!dataCheck(birthday)&&birthday.length!=0) {
            showError("日期格式应为 xxxx-xx-xx<br>或 xxxx-x-x",2000);
            return false;
        }else if (birthday.length!=0) {
            userEdittingInfo.birthday = birthday;
        };

        if (address.length!=0) {
            userEdittingInfo.address = address;
        };
        $.post("/u/info",userEdittingInfo,function(a){
            self.location = location.pathname;
        });
        return false;
    });

    // create opus series
    $("#createOpusSeries").click(function(){
        $(".opusSeriesEdit").show();
        $("#opusSeriesEditTitle").val("");
        $("#opusSeriesEditDescription").val("");
        $("#selectedOpusListWrap").empty();
        $("#opusSeriesEditPart1").show();
        $("#opusSeriesEditPart2").hide();
        updateOpusNum();
        return false;
    });
    $("#opusSeriesEditNext").click(function(){
        if ($("#opusSeriesEditTitle").val().length==0) {
            showError("请填写作品系列标题",2000);
            return false;
        };
        if ($("#opusSeriesEditTitle").val().length>30) {
            showError("作品系列标题超过规定字数上限",2000);
            return false;
        };
        if ($("#opusSeriesEditDescription").val().length>500) {
            showError("作品系列简介超过规定字数上限",2000);
            return false;
        };
        $("#opusSeriesEditPart1").slideUp();
        $("#opusSeriesEditPart2").slideDown();
        return false;
    });
    $("#opusSeriesEditPre").click(function(){
        $("#opusSeriesEditPart2").slideUp();
        $("#opusSeriesEditPart1").slideDown();
        return false;
    });
    $(".closeOpusSeriesEdit").click(function(){
        $(".opusSeriesEdit").fadeOut();
        return false;
    });
    // submit opusSeries
    $("#opusSeriesEditFinish").click(function(){
        if ($("#opusSeriesEditTitle").val().length==0) {
            showError("请填写作品系列标题",2000);
            return false;
        };
        if ($("#opusSeriesEditTitle").val().length>30) {
            showError("作品系列标题超过规定字数上限",2000);
            return false;
        };
        if ($("#selectedOpusListWrap").children().size()==0) {
            showError("请选择作品",2000);
            return false;
        };
        var opusSeriesOpusList=[];
        for(var i=0;i<$("#selectedOpusListWrap").children().size();i++){
            var opusID=parseInt($("#selectedOpusListWrap").children().eq(i).attr("id").slice(4));
            opusSeriesOpusList.push(opusID);
        }
        var opusSeriesEditData={
            'opusSeriesTitle':$("#opusSeriesEditTitle").val(),
            'opusSeriesDescription':$("#opusSeriesEditDescription").val(),
            'opusSeriesOpusList':opusSeriesOpusList
        };
        console.log(opusSeriesEditData);
        $(".opusSeriesEdit").hide();
        return false;
    });
    $(".editOpusSeries").click(function(){
        $("#selectedOpusListWrap").empty();
        $("#opusSeriesEditPart1").show();
        $("#opusSeriesEditPart2").hide();
        var opusSeriesTitle=$(this).prev().text(),
        opusSeriesDescription=$(this).next().next().children(".opusSeriesDescription").text();
        for(var i=0;i<$(this).next().next().children(".opusSeriesExpandList").size();i++){
            var opusID="opus"+i;
            var opusTitle=$(this).next().next().find(".opusSeriesExpandTitle").eq(i).text();
            var app='<li class="availableOpusList" draggable="true" ondragstart="drag(event)" ondblclick="dropThisOpus(this)" id="'+opusID+'">'+opusTitle+'</li>';
            $("#selectedOpusListWrap").append(app);
        };
        $("#opusSeriesEditTitle").val(opusSeriesTitle);
        $("#opusSeriesEditDescription").val(opusSeriesDescription);
        $(".opusSeriesEdit").show();
        updateOpusNum();
        return false;
    });
    $(".expandOpusSeries").click(function(){
        if ($(this).next().css("display")=="none") {
            $(this).next().show();
            $(this).text("收起");
        }else{
            $(this).next().hide();
            $(this).text("展开");
        };
        return false;
    });
    $(".forMore").click(function(){
        var parentName=$(this).prev().attr("id");
        loadingShow("#"+parentName);
        $(this).hide();
        setTimeout(function(){
            testLoad("#"+parentName);
            $("#"+parentName).next().show();
        },2000);
        return false;
    });
});

function checkSex(){
    if ($("#edittingSexMale").prop('checked')) {
        return true;
    }else if ($("#edittingSexFemale").prop('checked')) {
        return false;
    };
    return;
}

function threePartHeight(){
    var userHomeInnerHeight=$(".userHomeInner").height();
    $(".userInfo,.myOpus,.myGroup").height(userHomeInnerHeight);
}

function allowDrop(ev){
    ev.preventDefault();
}

function drag(ev){
    ev.dataTransfer.setData("Text",ev.target.id);
}

function drop(ev){
    ev.preventDefault();
    var data=ev.dataTransfer.getData("Text");
    if (ev.target.nodeName=="LI") {
        ev.target.parentNode.insertBefore(document.getElementById(data),ev.target);
        return;
    };
    ev.target.appendChild(document.getElementById(data));
    updateOpusNum();
}

function dropThisOpus(opus){
    var opusID=opus.getAttribute("id");
    if(opus.parentNode.getAttribute("id")=="availableOpusListWrap"){
        document.getElementById("selectedOpusListWrap").appendChild(opus);
    }else{
        document.getElementById("availableOpusListWrap").appendChild(opus);
    };
    updateOpusNum();
    return false;
}

function updateOpusNum(){
    $("#selectedOpusNum").text($("#selectedOpusListWrap").children().size());
    $("#availableOpusNum").text($("#availableOpusListWrap").children().size());
}

function dataCheck(dataStr){
    if (dateRe.test(dataStr) || dateLessRe.test(dataStr)) {
        return true;
    };
    return false;
}



