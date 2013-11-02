梧桐
================
文章分享网站  
#安装  
\#创建数据库wutong  
`createdb wutong`  
\#进入wutong  
`pqsl wutong`  
\#执行db.sql文件中的所有sql语句  
`\i db.sql`  
\#运行测试用例，其作用包括：删除所有数据，插入测试数据  
`python test.py`  
\#运行梧桐，默认url为：127.0.0.1:8888  
`python main.py`  

#group需要post的东西01
\#chat 用户名 内容 （后台记录时间，头像暂不post）
\#topic 用户名 标题 内容 （后台记录时间，头像暂不post）
#group需要get的东西01
\#login 用户名
\#chat 用户名 内容 时间
\#topic 用户名 标题 内容 时间
