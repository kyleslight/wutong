$(document).ready(function(){
   $("#searchAdvancedButton").click(function(){
        $(".searchAdvancedFliter").fadeToggle("slow");
        if ($(this).text()=="高级选项") {
            $(this).text("收起高级选项");
        }else{
            $(this).text("高级选项");
        }
   }); 
});



