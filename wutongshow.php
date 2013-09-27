<head> 
<link type="text/css" rel="stylesheet" href="shCoreDefault.css"/>
<script src="shCore.js" ></script>
<script src="all.js" ></script>
<script type="text/javascript">SyntaxHighlighter.all();</script>
</head>
<?php
	header('Content-Type: text/html; charset=utf-8');
	echo "<h2>You have posted:</h2><hr/>".$_POST['title']."<hr/>".$_POST['describe']."<hr/>".stripslashes($_POST["textArea"]);
?>