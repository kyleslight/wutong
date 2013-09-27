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

