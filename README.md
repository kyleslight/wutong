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

