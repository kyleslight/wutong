<head> 
<script type="text/javascript" src="scripts/shCore.js"></script>
	<script type="text/javascript" src="scripts/allhl.js"></script>
	<link type="text/css" rel="stylesheet" href="css/shCoreDefault.css"/>
	<script type="text/javascript">SyntaxHighlighter.all();</script>
</head>

<?php
	header('Content-Type: text/html; charset=utf-8');
	echo "<h2>You have posted:</h2><hr/>".$_POST['title']."<hr/>".$_POST['describe']."<hr/>".stripslashes($_POST["textArea"]);
?>