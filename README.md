梧桐
================
文章分享网站  

#依赖  
python2.7  
[python-memcached](https://github.com/linsomniac/python-memcached)    
python-tornado  
python-psycopg2  
postgresql-9.2  
postgresql-contrib-9.2  
[memcached](http://memcached.org/)  

#安装  
\#创建数据库wutong  
`createdb wutong`  
`createdb wutong_test`  
`psql wutong`  
`CREATE EXTENSION pgcrypto;`  

#运行   
\#运行梧桐，默认url为：127.0.0.1:8888  
`memcached`
`python model/test_model.py`  
`python main.py`  
