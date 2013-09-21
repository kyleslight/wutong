var $activeparti;

//Level 1 function
$(document).ready(function(){
	$activeparti=$(".answer");
	$activeparti.hide();
	$activeparti=$(".ansback");
	$activeparti.hide();
})

function showfundis(disid){
	var x=document.getElementById("fundis");
	switch(disid){
		case 1:x.innerHTML="浏览文章及其他梧桐资讯";break;
		case 2:x.innerHTML="编写与发表文章";break;
		case 3:x.innerHTML="记录下每天生活的点滴";break;
		case 4:x.innerHTML="记录琐碎的灵感";break;
		case 5:x.innerHTML="加入小组，开始寻找志同道合者与项目伙伴";break;
		case 6:x.innerHTML="将最近感兴趣的作品推荐给他人";break;
		case 7:x.innerHTML="产品&小制作发布平台";break;
	}
	$activeparti=$(".fundis");
	$activeparti.css({"opacity":"0.0"});
	$activeparti.animate({opacity:1.0},2000);
}

function fadefundis(){
	var x=document.getElementById("fundis")
	x.innerHTML="欢迎来到梧桐";
	$activeparti=$(".fundis");
	$activeparti.css({"opacity":"0.0"});
	$activeparti.animate({opacity:1.0},2000);
	$activeparti.stop();
}

function showans(ansid){
	$activeparti=$(".questions");
	$activeparti.animate({right:'250px'},1000);
	$activeparti=$("#answer"+ansid);
	$activeparti.show();
	$activeparti=$(".answers");
	$activeparti.animate({right:'130px'},1000);
	$activeparti=$(".ansbackcon");
	$activeparti.animate({right:'200px'},800,function(){$activeparti=$(".ansback");$activeparti.show();});
}

function ansback(){
	$activeparti=$(".answer");
	$activeparti.hide();
	$activeparti=$(".answers");
	$activeparti.animate({right:'0'},1000);
	$activeparti=$(".questions");
	$activeparti.animate({right:'0'},1000);
	$activeparti=$(".ansbackcon");
	$activeparti.animate({right:'0'});
	$activeparti=$(".ansback");
	$activeparti.hide();
}

function showpart(partid){
	//delete all unnecessary items,such as workmap0x,workmapfade,welcome classes,and delete button
	$activeparti=$(".introimg,#delete,.mainview,.welcome");
	clearitem();
	//redraw the introcharactor and workshow
	$activeparti=$("#introimg"+partid+",#workshow"+partid);
	$activeparti.animate({opacity:1.0},1000);
	$activeparti.css({"z-index":"1"});
	//delete the workmap and workmapfade
	$activeparti=$("workmapfade,workmap"+partid);
	clearitem();
}

function showintro(id,bgid) {
	//delete all unnecessary items,such as workmap0x,workmapfade classes,and delete button
	$activeparti=$(".workmap" + bgid +",.workmapfade,#delete");
	clearitem();
	//redraw the workmap
	$activeparti=$("#workmap0" + id);
	$activeparti.animate({opacity:1.0},2000);
	$activeparti.css({"z-index":"2"});
	//redraw the workmapfadebg
	$activeparti=$("#workmapfadebg" + bgid);
	$activeparti.animate({opacity:0.0},1500);
	$activeparti.animate({opacity:1.0},2000);
	$activeparti.css({"z-index":"3"});
	//redraw the workmapfade
	$activeparti=$("#workmapfade0" + id);
	$activeparti.animate({opacity:0.0},1500);
	$activeparti.animate({opacity:1.0},2000);
	$activeparti.css({"z-index":"4"});
	//redraw the delete button
	$activeparti=$("#delete");
	$activeparti.animate({opacity:1.0},3500);
	$activeparti.css({"z-index":"4"});
}

function showwel(welid){
	//get the next id of welcome
	var welnext=welid+1;
	$activeparti=$("#wel" + welid);
	//the activie wel slides
	$activeparti.animate({left:'596px'},1000);
	$activeparti.animate({opacity:0.0},1500);
	$activeparti.css({"z-index":"0"});
	//the next activie wel show
	$activeparti=$("#wel" + welnext);
	$activeparti.css({"z-index":"1"});
	$activeparti.animate({opacity:1.0},2000);
	//while welid is 3,show the map
	if (welid==3) {
		$activeparti=$("#wel7");
		$activeparti.css({"z-index":"7"});
		$activeparti.animate({opacity:1.0},2000);
	}
	//while welid is 4,fade the map
	else if (welid==4) {
		$activeparti=$("#wel7");
		$activeparti.css({"z-index":"4"});
		$activeparti.animate({opacity:0.0},500);
	};
}

function closefade(){
	/*delete the workmapfade and delete button*/
	$activeparti=$(".workmapfade,#delete");
	clearitem();
}

//Level 2 function

function clearitem(){
	$activeparti.animate({opacity:0.0},10);
	$activeparti.css({"z-index":"0"});
}

function loadimg(){
	for (var j = 0; j <4; j++) {
		var k=j+1;
		var ch=$(".workmap0"+k);
		for (var i = 0; i < ch.length; i++) {
			var s=i+1;
			if (s<10) {
				ch[i].src='image/dd0'+s+'.png';
				ch[i].id='workmap010'+s;
			}
			else{
				ch[i].src='image/dd'+s+'.png';
				ch[i].id='workmap01'+s;
			}
		}
	}
}

function checkDate(){
	var dateFlag;
	if (!document.getElementById||!document.createTextNode) {return};
	var dateField=document.getElementById('date');
	if (!dateField) {return};
	var errorContainer=dateField.parentNode.getElementsByTagName('span')[0];
	if(!errorContainer){return};
	var checkPattern=new RegExp("\\d{2}/\\d{2}/\\d{4}");
	var errorMessage="";
	errorContainer.firstChild.nodeValue="";
	var dateValue=dateField.value;
	if (dateValue=="") {
		errorMessage="Please provide a date.";
		dateFlag=false;
	}
	else if (!checkPattern.test(dateValue)) {
		errorMessage="Please provide the date in the defined format.";
		dateFlag=false;
	}
	if (dateFlag==false) {
		errorContainer.firstChild.nodeValue=errorMessage;
		dateField.focus();
		return false;
	}
	else{
		return true;
	}
}

window.onload=loadimg;

