#配置
__`sh configure.sh [run|unittest|testdata|updatedb|clean]`__
 * [运行服务器](http://127.0.0.1:8888)
   `sh configure.sh run`
 * 运行单元测试
   `sh configure.sh unittest`
 * 单独更新数据库
   `sh configure.sh updatedb`
 * 生成测试用例
   `sh configure.sh testdata`
 * 添加10个测试用户
   `sh configure.sh testdata 10`

####coreseek的安装
#####依赖
 * gcc
 * autoconf-2.65
 * automake-1.11
 * libtool-2.2.6b
 * m4-1.4.13
 * sphinxexpr.cpp_.patch_.zip

#####配置
将`coreseek`目录下的文件移到对应的`coreseek`安装目录下(可能为/usr/local/coreseek)

####环境变量
 * WUTONG_EMAIL_SMTP
 * WUTONG_EMAIL_ADDR
 * WUTONG_EMAIL_PASSWD
 * WUTONG_DB
 * WUTONG_DB_HOST
 * WUTONG_DB_PORT
 * WUTONG_DB_USER
 * WUTONG_DB_PASSWD

#依赖
 * python-tornado
 * python-psycopg2
 * tornado-redis
 * redis
 * postgresql-9.2
 * postgresql-contrib-9.2
 * coreseeek-4.1-beta

#API
__错误信息都是json, 格式为`{"msg": err, "errno": num}`__
```
if errno == 0:
    msg 是 携带的正常信息
else if errno > 0:
    msg 是 出错信息
    errno 是 对应的出错码
else:
    msg 是 出错信息
    errno 未设定
```
