var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
$(document).ready(function(){
    // basic
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

    $("#return_top").click(function(){
        $('html,body').animate({scrollTop:0},1000);
        return false;
    });
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
    })

    $(".opusTypeItem").click(function(){
        $(".opusTypeItem").css({"color":"#555","font-size":"1em"});
        $(this).css({"color":"#680","font-size":"35px"});
    })

    $(".opusClassItem").click(function(){
        $(".activeOpusClassItem").removeClass("activeOpusClassItem");
        $(this).addClass("activeOpusClassItem");
    })

});



