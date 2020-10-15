# Web应用部署（bottle+uwsgi+nginx）
项目实现功能文档自助发送，自助提取；熟悉web应用部署操作；


开发过程说明：

使用bottle框架开发了一个文档软件自助提取的网站。代码开发完成后，本地测试没有问题，但上线之后非常不稳定，网站使用一段时间后自己卡死了（多个访问造成进程阻塞）。查找原因发现，bottle自建web应用不适合用于生产环境，稳定性比较差。使用uwsgi+nginx，web应用会更加安全稳定，性能更优。

至于为什么用bottle，是因为手头有个之前自己开发的现成网站代码，当时就是用bottle写的，懒得改；Python版本是3.6.8；服务器是花98块买的阿里云ecs，买来玩的。

由于以前没用过uwsgi/nginx，而且网上关于bottle框架下应用uwsgi/nginx部署的资源很少（确实少，中文英文的都少），资料看起来非常费劲，研究了两天总算把这事理了大概，跑起来了。

项目详细情况如下：

##0. 系统环境及软件版本说明
```
[root@aliyun ~]# uname -a
Linux aliyun 4.18.0-147.5.1.el8_1.x86_64 #1 SMP Wed Feb 5 02:00:39 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
[root@aliyun ~]# python3 --version
Python 3.6.8
[root@aliyun ~]# uwsgi --version
2.0.19.1
[root@aliyun ~]# nginx -v
nginx version: nginx/1.14.1
[root@aliyun ~]# pip3 show bottle
Name: bottle
Version: 0.12.18
Summary: Fast and simple WSGI-framework for small web-applications.
Home-page: http://bottlepy.org/
Author: Marcel Hellkamp
Author-email: marc@gsites.de
License: MIT
Location: /usr/local/lib/python3.6/site-packages
Requires: 
[root@aliyun ~]# cd /var/www/html/WEB_TRANSFER_DOCUMENTS/
[root@aliyun WEB_TRANSFER_DOCUMENTS]# ls
50x.html  download         error.txt  __pycache__  reload   test.py    webpage
data      Email_Custom.py  main.py    records.csv  run.log  uwsgi.ini
[root@aliyun WEB_TRANSFER_DOCUMENTS]# 
```
##1. uwsgi配置文件：uwsgi.ini

文件路径：/var/www/html/WEB_TRANSFER_DOCUMENTS 

log路径：/var/www/html/WEB_TRANSFER_DOCUMENTS/run.log
```
[uwsgi]
chdir = /var/www/html/WEB_TRANSFER_DOCUMENTS
socket =0.0.0.0:8129
master = true
worker = 4
wsgi-file=main.py
callable=application
enable-threads = true
py-autoreload= 1
processes = 8
threads =1
daemonize = /var/www/html/WEB_TRANSFER_DOCUMENTS/run.log                                                       
```
##2.  Nginx 配置文件：nginx.conf

文件路径：/etc/nginx/nginx.conf

access log路径：/var/log/nginx/access.log

error log路径：/var/log/nginx/error.log
```
# For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen       80 default_server;
        listen       [::]:80 default_server;
        server_name  www.creditlife.top;
        root         /var/www/html/WEB_TRANSFER_DOCUMENTS;
	proxy_connect_timeout 600;
	proxy_read_timeout 600;
	proxy_send_timeout 600;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
		uwsgi_pass 0.0.0.0:8129;
		include uwsgi_params;
		uwsgi_send_timeout 600;
		uwsgi_connect_timeout 600;
		uwsgi_read_timeout 600;
        }

        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }
    }
}
```
##3. bottle app 主程序代码：main.py
```
# -*- coding: utf8 -*-
from bottle import run, route, static_file,request,template,default_app,response,redirect
import random,Email_Custom
from collections import defaultdict
import csv,datetime,bottle,traceback

user_information = {}
paths = {}
with open('data/data_sources.csv','r') as f:
    content = csv.reader(f)
    for items in content:
        paths[items[0].strip()] =items[1:]

@route('/counter')
def counter():
    try:
        count = int(request.cookies.get('counter_test', '0'))
        count += 1
        response.set_cookie('counter_test', str(count))
        return 'You visited this page %d times' % count
    except :
        traceback.print_exc(file=open('error.txt','a'))

@route('/')
def index():
    return static_file('index.html', root='./webpage')

@route('/feedback/<path>')
def feedback(path):
    return static_file(path, root='./webpage/feedback')

@route('/<path>')
def webpage_root(path):
    return static_file(path, root='./webpage')

@route('/download/<path>')
def download_display(path):
    return static_file(path, root='./download',download=path)

@route('/images/<path>')
def images(path):
    return static_file(path, root='./webpage/images')

@route('/assets/css/<path>')
def css_display(path):
    return static_file(path, root='./webpage/assets/css')

@route('/assets/js/<path>')
def js_display(path):
    return static_file(path, root='./webpage/assets/js')
@route('/assets/fonts/<path>')
def fonts_display(path):
    return static_file(path, root='./webpage/assets/fonts')
@route('/robots')
def submit_get_mails():
    try:
        mail_address = request.query.email.strip()
        user_ip = request.remote_addr
        #response.set_cookie('param',mail_address,path='/documents')
        user_information[user_ip] = mail_address
        with open('records.csv','a',newline='') as code:
            m = csv.writer(code,dialect='excel')
            m.writerow([datetime.datetime.now().strftime('%Y-%m-%d'),datetime.datetime.now().strftime('%H:%M:%S'),user_ip,mail_address])
        return static_file('document_choose.html', root='./webpage')
    except Exception as e:
        traceback.print_exc(file=open('error.txt','a'))
        return 'something wrong'

@route('/documents')
def submit_get_document_number():
    document_number = request.query.theone
    user_ip = request.remote_addr
    try:
        #count = request.cookies.get('param')
        thepaths = paths[document_number]
        if thepaths:
            flag = Email_Custom.sendEmail(mail_address,authorization——code,thepaths[0].strip(),open(thepaths[2],'rb').read(),user_information[user_ip],thepaths[1]) #前两个参数为个人邮箱地址和授权码，需自行补充添加。
            if flag:
                return '<p style=\"width:100%;font-size: 45px;text-align:center;margin-top:20%;\"><p style=\"color: crimson;\">'+user_information[user_ip]+'</p>你好，资料已发送，请注意查收！</p>'
            else:
                return '<p style=\"width:100%;font-size: 45px;text-align: center; margin-top: 20%;color: crimson;\">邮箱地址异常，发送失败；请检查邮箱地址后重试！</p>'
    except Exception as e:
        traceback.print_exc(file=open('error.txt','a'))
        with open('error.txt','a') as code:
            code.write("错误信息："+str(e)+'，来访地址：'+user_ip+ "\n")
        return '<p style=\"width:100%;font-size: 45px;text-align:center;margin-top:20%;color: crimson;\">发送失败。请清除缓存后重试！<br><br>如多次重试失败，请联系微信:hylan129</p>'
@route('/try')
def submit_try():
    return "<html><img src=\"images/slide05.jpg\" /></html>"

if __name__ == '__main__':
    run(host="0.0.0.0", port=8129,debug=False,reloader=True)
else:
    application = default_app()
```
 ##4. 部署相关说明
 ```
    1、bottle app 主程序中必须包含application函数，'application'名字固定，否则uwsgi 启动时会出现no app loaded 错误；
    2、uwsgin配置时callable=application 不能少；配置端口时采用socket，socket = 0.0.0.0:8129；如果使用http，则是将uwsgi直接当作服务器使用，没法连接nginx；
    3、uwsgi配置中参数daemonize建议配置，daemonize = /var/www/html/WEB_TRANSFER_DOCUMENTS/run.log；uwsgi程序后置后台运行同时指定日志路径，方便查看异常错误；
    4、uwsgi参数众多，可以使用uwsgi -h命令查看相关帮助文档。
    5、nginx配置文件路径不要改（建议直接在原始配置文件中更改），nginx.conf文件在nginx安装后会自动生成，而且安装完成后会提示配置文件的路径。
    6、nginx配置文件中，只需要更新listen、server_name、root、uwsgi_pass、include参数即可。其他参数根据需要以及出错问题再补充；（因为我的程序后台耗时比较久，出现过超时错误，后来我增加了多个timeout参数）
    7、命令运行顺序：uwsgi --ini uwsgi.ini &  nginx，或者逐个命令运行；
    8、使用uwsgi服务，不需要单独启动main.py（python main.py不需要）；
    9、部署过程中可以查看log确认具体问题，uwsgi log：/var/www/html/WEB_TRANSFER_DOCUMENTS/run.log；nginx log：/var/log/nginx/error.log；
    10、web应用部署涉及使用两个端口，nginx配置的是外网访问http端口，即listen端口号；uwsgi 配置端口为uwsgi与nginx socket连接端口，即uwsgi参数：socket=0.0.0.0:8129;nginx参数：uwsgi_pass 0.0.0.0:8129;bottle app main.py中配置端口与uwsgin端口号相同，即run(host="0.0.0.0", port=8129);
```
##5. web应用源码
 登录[creditlife.top](www.creditlife.top)网站提供邮箱地址即可下载获取。
***
***
参照文章：[1：django为什么用uwsgi+nginx](https://blog.csdn.net/qq_35318838/article/details/61198183?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~sobaiduend~default-1-61198183.nonecase&utm_term=uwsgi%20和直接运行区别&spm=1000.2123.3001.4430) ；[2：python web服务部署](https://blog.csdn.net/Together_CZ/article/details/105518419)
