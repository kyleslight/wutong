function ajaxFileUpload(fileBox){
	$.ajaxFileUpload({
        url:'/upload', 
        secureuri:false,
        fileElementId:fileBox,
        dataType: 'json',
        success: function (data){
            alert(data.file_infor);
        }
    })

	return false;
} 