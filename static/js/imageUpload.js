/* global variants */
var queueid=0,
queue = new Array(),
working = 0,
msgqueue = new Array();
// for image upload
ui_msg = {
    err: {
        illegal_url: '不是合法的URL。',
        fail_load: '无法加载预览，等待服务器响应。',
        wrong_type: '文件格式不支持',
        size_limit: '超出文件大小限制',
        no_file: '无法被服务器获取，请检查URL是否正确。',
        write_prohibited: '无法存储到服务器。',
        fail_duplicate: '无法进行重复文件检查。',
        php_upload_size_limit: '超出php.ini中设置的大小限制。',
        part_upload: '只有部分被上传。',
        no_tmp: '服务器没有临时目录',
        fail_retry: '多次重试均失败。'
    },
    err_detail: {
        no_file: '文件无法被服务器获取，可能远程服务器无法访问，或者文件不再存在，或者你输入的URL有错误。',
        size_limit: '超过文件大小限制。',
        fail_load: '文件预览无法加载，可能文件不存在，或者远程服务器无法访问，或者你输入的URL有错误。',
        write_prohibited: '文件无法写入服务器的上传目录，请联系网站管理员检查权限设置。',
        wrong_type: '文件格式当前无法支持，请联系程序作者获取帮助。',
        fail_duplicate: '无法进行重复文件检查。',
        php_upload_size_limit: '超过php.ini中设定的文件大小限制',
        part_upload: '文件只有部分被上传，请重新上传。',
        no_tmp: '服务器上不存在临时目录，请联系网站管理员检查。',
        fail_retry: '多次尝试上传但均告失败。'
    },
    status: {
        prepare: '准备上传',
        waiting: '等待上传',
        uploading: '上传中',
        success: '上传成功',
        error: '发生错误',
        failed: '上传失败',
        all_success: '所选文件均成功上传',
        part_success: '所选部分文件没有成功上传，仅成功上传的会在下方显示',
        all_failed: '所选文件均上传失败',
    },
    info: {
        selected: '已选择',
        files_selected: '个文件被选择。',
        orig: '原始文件地址',
        html: 'HTML代码',
        html_with_thumb: '带有缩略图的HTML代码',
        bbcode: 'BBCode代码',
        bbcode_with_thumb: '带有缩略图的BBCode代码',
        thumb_tips: '点击显示原始图片'
    }
};
prop = {
    size_limit: 67108864,
    upload_count: 300
}

/* Handler for URL upload */
function url_upload_handler() {
	var urls = url_list.value.split('\n');
	for (var url,i=0;i<urls.length;i++) {
		url = urls[i].trim();
		var work = {
			type: 'url',
			path: url,
			status: 'prepared',
			retry: 0
		};
		if(!isempty(url)) {
			if (isurl(url)) {
				work.qid = queueid++;
				show_thumbnail(work);
				insertImageAll(work.path);
			}else {
				work.status = 'failed'
				work.err = 'illegal_url';
				show_error(work);
			}
		}
	}
}

/* Handler for file upload */
function file_upload_handler(files) {
	for(var file,i=0;i<files.length;i++) {
		file=files[i];
		work = {
			type: 'file',
			path: file.name,
			status: 'prepared',
			fileobj: file
		};
		if(!/image\/(jpeg|png|gif|svg\+xml)/.test(file.type)) {
			work.status = 'failed';
			work.err = 'wrong_type';
			show_error(work);
		}else if(file.size > prop.size_limit) {
			work.status = 'failed';
			work.err = 'size_limit';
			show_error(work);
		}else {
			work.qid = queueid++;
			show_thumbnail(work);
			upload(work);
		}
	}
}

/* Submit from */
function normal_upload_handler() {
	normal_form.submit();
}

/* Start upload or put in the queue */
function upload(work) {
	if (working < prop.upload_count) {
		select_upload(work);
	} else {
		work.status = 'waiting';
		queue.push(work);
	}
}

/* Upload next item in the queue */
function upload_next() {
	working--;
	if(queue.length>0) {
		work = queue.shift();
		select_upload(work);
	}
}

function retry_upload(work) {
	working--;
	work.retry++;
	if(work.retry < 3) {
		upload(work);
	}else {
		work.status = 'failed';
		work.err = 'fail_retry';
		show_error(work);
	}
}

/* Choose upload method */
function select_upload(work) {
	work.status = 'uploading';
	switch (work.type) {
		case 'url':
			url_upload(work);
			break;
		case 'file':
			file_upload(work);
			break;
	}
	working++;
}

/* Upload URL item */
function url_upload(work) {
	var self = document.getElementById('q'+work.qid);
	if(!self) {
		var callself = function(){url_upload(work);};
		setTimeout(callself,100);
		return false;
	}

	var xhr = new XMLHttpRequest();

	xhr.open('POST', 'api.php?type=url&'+(new Date()).getTime(), true);
	xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

	var sendData = 'qid='+work.qid+'&url='+encodeURIComponent(work.path);

	xhr.addEventListener('readystatechange', function(e){
		if(xhr.readyState == 4) {
			if(xhr.status == 200) {
				eval('var res = '+xhr.responseText);
				after_upload(res);
				upload_next();
			}else if(xhr.status == 504) {
				retry_upload(work);
			}
		}
	},false);

	xhr.upload.addEventListener('progress',function(e){
		if(e.lengthComputable) {
			var percentage = e.loaded/e.total;
			self.progress(percentage);
		}
	},false);
	xhr.upload.addEventListener('load',function(e){
		self.progress(1);
	},false);

	xhr.send(sendData);
}

/* Upload file item */
function file_upload(work) {
	var self = document.getElementById('q'+work.qid);
	if(!self) {
		var callself = function(){file_upload(work);};
		setTimeout(callself,100);
		return false;
	}
	var xhr = new XMLHttpRequest();
	var fd = new FormData();

	xhr.open('POST', '/upload', true);
	// xhr.setRequestHeader("Content-type", "multipart/form-data");

	xhr.addEventListener('readystatechange', function(e){
		if(xhr.readyState == 4) {
			if(xhr.status == 200) {
				var imageUploadUrl='/static/uploads/'+xhr.responseText;
				insertImageAll(imageUploadUrl);
			}
		}
	},false);

	xhr.upload.addEventListener('progress',function(e){
		if(e.lengthComputable) {
			var percentage = e.loaded/e.total;
			self.progress(percentage);
		}
	},false);
	xhr.upload.addEventListener('load',function(e){
		self.progress(1);
	},false);

	fd.append('qid',work.qid);
	fd.append('file',work.fileobj);

	xhr.send(fd);
}

/* Check if valid URL */
function isurl(theurl) {
	return /^\s*https?:\/\/.+$/.test(theurl);
}

/* Check if empty URL */
function isempty(theurl) {
	return (/^\s*$/.test(theurl) || theurl=='');
}

function after_upload(res) {
	var qli = document.getElementById('q'+res.qid);
	var qimg = qli.children[0];
	var qprg = qimg.children[0];
	var qsel = qprg.children[0];
	if(!qli) {
		var callself = function(){after_upload(res);};
		setTimeout(callself,100);
		return false;
	}
	switch (res.status) {
		case 'success':
			qli.work.status = 'success';
			qli.work.name = res.name;
			qli.work.path = res.path;
			qli.work.thumb = res.thumb;
			if(res.thumb=='none') {
				qimg.style.backgroundImage = 'url("'+res.path+'")';
			}else {
				qimg.style.backgroundImage = 'url("'+res.thumb+'")';
			}
			break;
		case 'error':
			qli.work.status = 'error';
			qli.work.err = res.err;
			qli.work.name = res.name;
			qli.work.path = res.path;
			qli.work.thumb = res.thumb;
			if(res.thumb=='none') {
				qimg.style.backgroundImage = 'url("'+res.path+'")';
			}else {
				qimg.style.backgroundImage = 'url("'+res.thumb+'")';
			}
			break;
		case 'failed':
				qli.work.status = 'failed';
				qli.work.err = res.err;
				qimg.style.backgroundImage = 'url(upload_error.png)';
				qimg.style.backgroundSize = '200px 200px';
				qimg.style.width = qprg.style.width = qli.style.width = '200px';
				qimg.style.height = qprg.style.height = qli.style.height = '200px';
				qli.style.marginTop = qli.marginBottom = '0';
				qsel.style.paddingTop = '170px';
				show_error(qli.work);
			break;
	}
	changeinfo(true);
}

function insertImageAll(imgUrl){
	switch(insertImageState){
					case 0:
					editor.execCommand( 'insertimage', {
			         	src:imgUrl
			    	} );break;
			    	case 1:
			    	// console.log(imgUrl);
			    	var imgUrlStr="'"+imgUrl+"'";
				    var appImage='<div class="preImageUpload" id="'+imgUrl+'">'
			                     +  '<img src="'+imgUrl+'" />'
			                     +  '<textarea class="preImageIntro input"></textarea>'
			                     +   '<div class="preImageUploadFunction">'
			                     +       '<a href="javascript:void(0);" class="deletePreImage" onclick="deletePreImage(this)">删除</a><a href="javascript:void(0);" class="addPreImageIntro" onclick="imageIntro(this)">图片说明</a>'
			                     +       '<a href="javascript:void(0);" class="moveup" onclick="imageMoveUp('+imgUrlStr+')">上移</a><a href="javascript:void(0);" class="movedown" onclick="imageMoveDown('+imgUrlStr+')">下移</a>'
			                     +   '</div>'
			                     +'</div>';
			        $("#preImageContainer").append(appImage);break;
			    	case 2:
			    	BCeditor.execCommand( 'insertimage', {
			         	src:imgUrl
			    	} );break;
			    	case 4:
			    	editor.execCommand( 'insertimage', {
			         	src:imgUrl
			    	} );break;
				}
	$("#first_load,#result_zone,#message_zone,.mask,#uploadImageBack,#main").hide();
}

function deletePreImage(deleteObj){
	deleteObj.parentNode.parentNode.remove();
}

function imageIntro(imageIntro){
	if (imageIntro.parentNode.previousSibling.style.display!="block") {
		imageIntro.parentNode.previousSibling.style.display="block";
	}else{
		imageIntro.parentNode.previousSibling.style.display="none";
	}
}

function imageMoveUp(imgUrl){
	var upImage=$("[id='"+imgUrl+"']");
	var upImageIndex=$(".preImageUpload").index(upImage);
	
	if (upImageIndex==0) {
		alert("已经是第一张图片");
		return;
	};
	upImage.prev().before(upImage.clone());
	upImage.remove();
}

function imageMoveDown(imgUrl){
	var upImage=$("[id='"+imgUrl+"']");
	var upImageIndex=$(".preImageUpload").index(upImage);
	if (upImageIndex==($(".preImageUpload").size()-1)) {
		alert("已经是最后一张图片");
		return;
	};
	upImage.next().after(upImage.clone());
	upImage.remove();
}
	
