// function iFrameOn(){
// 	richTextField.document.designMode='on';
// }

// function iBold(){
// 	richTextField.document.execCommand('bold',false,null);
// }

// function iUnderLine(){
// 	richTextField.document.execCommand('Underline',false,null);
// }

// function iItalic(){
// 	richTextField.document.execCommand('Italic',false,null);
// }

// function iFontSize(){
// 	var size=prompt("enter a number",'');
// 	richTextField.document.execCommand('FontSize',false,size);
// }

// function iFontColor(){
// 	var color=prompt("enter a color",'');
// 	richTextField.document.execCommand('ForeColor',false,color);
// }

// function iMR(){

// }

// function iUnorderedList(){

// }

// function iOrderedList(){

// }

// function iLink(){
// 	var linkURL=prompt("enter a link",'http://');
// 	richTextField.document.execCommand('CreateLink',false,linkURL);
// }

// function iCode(){
// 	document.execCommand('InsertInputText',false,"aa");
// 	richTextField.document.execCommand('InsertTextArea',true,'textareaa');
// }
// function iImage(){
// 	var imageSrc=prompt('Enter image location:','');
// 	if (imageSrc!=null) {
// 		richTextField.document.execCommand('insertimage',false,imageSrc);
// 	};
// }

// function submit_form(){
// 	var theForm=document.getElementById("textdata");
// 	//theForm.elements['textArea'].value=window.frames['richTextField'].document.body.innerHTML;
// 	theForm.submit();
// }

// function load(){
// 	$('#loadbox').fadeIn();
// 	document.getElementById("graybg").style.display='block';
// 	document.getElementById("graybg").style.filter='alpha(opacity=50)';
// 	$('#graybg').height(document.body.scrollHeight);
//   	return false;
// }

// function loadback(){
// 	$('#loadbox').fadeOut();
// 	$('#graybg').fadeOut();
// 	return false;
// }

var isloadbox=false;
var isregisterbox=false;
var _showwel_flag = true;
var elapseTime = 5000;
$(document).ready(function(){
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

	
});



