$(document).ready(function(){
    threePartHeight();
    $(".opusPartButton").click(function(){
        $(".activeOpusPart").removeClass("activeOpusPart");
        var indexOfOpusPart=$(".opusPartButton").index($(this));
        $(".opusPart").eq(indexOfOpusPart).addClass("activeOpusPart");
        return false;
    });
    $(".opusCommentButton").click(function(){
        $(".activeOpusCommentButton").removeClass("activeOpusCommentButton");
        $(".activeOpusCommentPart").removeClass("activeOpusCommentPart");
        var indexOfOpusCommentPart=$(".opusCommentButton").index($(this));
        $(".opusCommentButton").eq(indexOfOpusCommentPart).addClass("activeOpusCommentButton");
        $(".opusCommentPart").eq(indexOfOpusCommentPart).addClass("activeOpusCommentPart");
        return false;
    });
});

function threePartHeight(){
    var userHomeInnerHeight=$(".userHomeInner").height();
    $(".userInfo,.myOpus,.myGroup").height(userHomeInnerHeight);
}



