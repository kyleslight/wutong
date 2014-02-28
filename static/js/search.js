$(document).ready(function() {
    $("#searchAdvancedButton").click(function() {
        $(".searchAdvancedFliter").fadeToggle("slow");
        if ($(this).text() == "高级选项") {
            $(this).text("收起高级选项");
        } else {
            $(this).text("高级选项");
        }
    });

    $(".searchType").click(function() {
        var query = $("#mainSearchBox").val();
        var id = $(this).attr('id');
        var type = id.replace('search_', '');
        $("#mainSearchType").val(type);
    });

    // TODO: 不新开标签页
    $("#mainSearchSubmitButton").click(function() {
        $("#mainSearchData").submit();
    });
});
