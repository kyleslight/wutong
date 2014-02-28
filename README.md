#配置
###`sh configure.sh [run|unittest|testdata|updatedb|clean]`
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

###coreseek的安装
####依赖
 * gcc
 * autoconf-2.65
 * automake-1.11
 * libtool-2.2.6b
 * m4-1.4.13
 * sphinxexpr.cpp_.patch_.zip
####配置
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
<table>
  <tr>
    <th>请求</th><th>作用</th><th>返回值</th><th>错误</th>
  </tr>
  <tr>
    <td>GET /account/check_username?v=wutong</td>
    <td>查询用户名是否存在</td>
    <td>{"msg": "1"/"0", "errno": "0"}</td>
    <td></td>
  </tr>
  <tr>
    <td>GET /account/check_email?v=wutong@qq.com</td>
    <td>查询email是否存在</td>
    <td>{"msg": "1"/"0", "errno": "0"}</td>
    <td></td>
  </tr>
  <tr>
    <td>GET /account/activate_account?v=someencrytedstring</td>
    <td>激活帐号</td>
    <td>json(user)</td>
    <td>'activate account failed'</td>
  </tr>
  <tr>
    <td>GET /u/info</td>
    <td>用户信息</td>
    <td>json(user)</td>
    <td>
    'need login'<br>
    'unknown error'
    </td>
</tr>
  <tr>
    <td>POST /u/info</td>
    <td>
    用户修改后的信息, <br>
    可选字段包括:<br>                 nickname<br>
    email<br>
    realname<br>
    phone<br>
    sex<br>
    birthday<br>
    address<br>
    intro<br>
    motto
    </td>
    <td></td>
    <td>
    'nickname exist'<br>
    'email exist'<br>
    'invalid nickname'<br>
    'invalid email'<br>
    ...
    </td>
  </tr>
  <tr>
    <td>GET /u/memo</td>
    <td>
    获取便笺, <br>
    可选字段示例:<br>
    GET /u/memo?id=1<br>
    GET /u/memo?page=1&size=10<br>
    </td>
    <td>json(user)</td>
    <td>
    'need login'<br>
    'unknown error'
    </td>
  </tr>
  <tr>
    <td>POST /u/memo</td>
    <td>
    操作便笺, <br>
    可选字段示例:<br>
    POST /u/memo?create&title=t&content=c<br>
    POST /u/memo?update&id=1&title=t&content=c<br>
    POST /u/memo?delete&id=1<br>
    </td>
    <td>json(memo)</td>
    <td>
    'need login'<br>
    'unknown error'
    </td>
  </tr>
</table>
