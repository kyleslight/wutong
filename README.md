#运行测试,添加测试数据
```bash
sh configure.sh test
```
默认只添加一个测试用户, 若想增加多个测试用户, 在后面添加参数, 如:
`sh configure.sh 10`

#运行
[访问地址 localhost:8888](http://127.0.0.1:8888)
`sh run.sh`

#依赖
 * python-tornado
 * python-psycopg2
 * postgresql-9.2
 * postgresql-contrib-9.2

#API
<table>
  <tr>
    <th>请求</th><th>作用</th><th>返回值</th>
  </tr>
  <tr>
    <td>/account/check?is_account_exists&v=wutong</td><td>查询用户名为wutong的帐号是否存在</td><td>true/false</td>
  </tr>
  <tr>
    <td>/account/check?activate_account_exists&v=573cf835c32b66ec5c0a6a0bd21103f8</td><td>激活帐号</td><td>/failed</td>
  </tr>
</table>
