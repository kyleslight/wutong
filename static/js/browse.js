var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
var indexOfOpusType=-1;
$(document).ready(function(){
    $("#artsubmitButton").click(function(){
        // with(this){
            with(arttitle){
                alert(value);
                return false;
            }
        // }
        var theForm=document.getElementById("textdata");
        theForm.submit();
    })
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
    })
    $(window).scroll(function(){
        scrollLoading(".opus");
    });

    $(".opusTypeItem").click(function(){
        if ($(".opusTypeItem").index($(this))==indexOfOpusType) {
            return;
        };
        indexOfOpusType=$(".opusTypeItem").index($(this));
        $(".opusTypeItem").css({"color":"#555","font-size":"20px"});
        $(this).css({"color":"#680","font-size":"35px"});
        $(".opusClassDivision").slideUp();
        $(".opusClassDivision").eq(indexOfOpusType).slideDown();
    })

    $(".opusClassItem").click(function(){
        $(this).siblings().removeClass("activeOpusClassItem");
        $(this).addClass("activeOpusClassItem");
    })

});



