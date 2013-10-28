function iFrameOn(){
	richTextField.document.designMode='on';
}

function iBold(){
	richTextField.document.execCommand('bold',false,null);
}

function iUnderLine(){
	richTextField.document.execCommand('Underline',false,null);
}

function iItalic(){
	richTextField.document.execCommand('Italic',false,null);
}

function iFontSize(){
	var size=prompt("enter a number",'');
	richTextField.document.execCommand('FontSize',false,size);
}

function iFontColor(){
	var color=prompt("enter a color",'');
	richTextField.document.execCommand('ForeColor',false,color);
}

function iMR(){

}

function iUnorderedList(){

}

function iOrderedList(){

}

function iLink(){
	var linkURL=prompt("enter a link",'http://');
	richTextField.document.execCommand('CreateLink',false,linkURL);
}

function iCode(){
	document.execCommand('InsertInputText',false,"aa");
	richTextField.document.execCommand('InsertTextArea',true,'textareaa');
}
function iImage(){
	var imageSrc=prompt('Enter image location:','');
	if (imageSrc!=null) {
		richTextField.document.execCommand('insertimage',false,imageSrc);
	};
}

function submit_form(){
	var theForm=document.getElementById("textdata");
	//theForm.elements['textArea'].value=window.frames['richTextField'].document.body.innerHTML;
	theForm.submit();
}

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
	$("#loadsubmitButton").click(function(){
		var theForm=document.getElementById("loadform");
		theForm.submit();
	})
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

	$("#load").click(function(){
		// $("#lrboxwrap").stop();
		// $("#registerbox").stop();
		// $("#loadbox").stop();
		if (_showwel_flag == true){
			_showwel_flag = false;
			setTimeout(function() {
				_showwel_flag = true;
			}, elapseTime);
			if (isregisterbox||isloadbox) {
				$("#loadbox,#registerbox").fadeOut(100,function(){$("#lrboxwrap").animate({height:"0px"},1000,function(){$("#lrboxwrap").fadeOut(200,function(){loadboxshow();});});})
			}else{
				loadboxshow();
			}
		}
		return false;
	});
    $("#loadback").click(function(){
    	loadboxfade();
    	isloadbox=false;
    	return false;
    });
    $("#register").click(function(){
    	if (_showwel_flag == true){
			_showwel_flag = false;
			setTimeout(function() {
				_showwel_flag = true;
			}, elapseTime);
	    	if (isregisterbox||isloadbox) {
	    		$("#loadbox,#registerbox").fadeOut(100,function(){$("#lrboxwrap").animate({height:"0px"},1000,function(){$("#lrboxwrap").fadeOut(200,function(){registerboxshow();});});});
	    	}else{
	    		registerboxshow();
	    	}
    	}
    	return false;
    })
    $("#registerback").click(function(){
    	registerboxfade();
    	isregisterbox=false;
    	return false;
    })
});

function loadboxshow(){
	$("#lrboxwrap").fadeIn(200);
	$("#lrboxwrap").animate({height:"200px"},1000,function(){$("#loadbox").fadeIn(200,function(){isloadbox=true;isregisterbox=false;});});
}

function loadboxfade(){
	$("#loadbox").fadeOut(200);
	$("#lrboxwrap").animate({height:"0px"},1000,function(){$("#lrboxwrap").fadeOut(500);});
}

function registerboxshow(){
	$("#lrboxwrap").fadeIn(200);
	$("#lrboxwrap").animate({height:"330px"},1000,function(){$("#registerbox").fadeIn(200,function(){isregisterbox=true;isloadbox=false;});});
}

function registerboxfade(){
	$("#registerbox").fadeOut(200);
	$("#lrboxwrap").animate({height:"0px"},1000,function(){$("#lrboxwrap").fadeOut(500);});	
}


