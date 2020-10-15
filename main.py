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
def webpage(path):
    return static_file(path, root='./download',download=path)

@route('/images/<path>')
def images(path):
    return static_file(path, root='./webpage/images')   
 
@route('/assets/css/<path>')
def css1(path):
    return static_file(path, root='./webpage/assets/css')

@route('/assets/js/<path>')
def js2(path):
    return static_file(path, root='./webpage/assets/js')
@route('/assets/fonts/<path>')
def fonts(path):
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
            flag = Email_Custom.sendEmail(mail_address, authorization_code,thepaths[0].strip(),open(thepaths[2],'rb').read(),user_information[user_ip],thepaths[1])
            if flag:
                return '<p style=\"width:100%;font-size: 45px;text-align:center;margin-top:20%;\"><p style=\"color: crimson;\">'+user_information[user_ip]+'</p>你好，资料已发送，请注意查收！</p>'
            else:
                return '<p style=\"width:100%;font-size: 45px;text-align: center; margin-top: 20%;color: crimson;\">邮箱地址异常，发送失败；请检查邮箱地址后重试！</p>'
    except Exception as e:
        traceback.print_exc(file=open('error.txt','a'))
        with open('error.txt','a') as code:
            code.write("错误信息："+str(e)+'，来访地址：'+user_ip+ "\n")
        return '<p style=\"width:100%;font-size: 45px;text-align:center;margin-top:20%;color: crimson;\">发送失败。请清除缓存后重试！<br><br>如多次重试失败，请联系微信:hylan129</p>'
        #return redirect('http://www.baidu.com') #重定向外链
@route('/try')
def submit_try():
    return "<html><img src=\"images/slide05.jpg\" /></html>"

if __name__ == '__main__':
    run(host="0.0.0.0", port=8129,debug=False,reloader=True)
else:
    application = default_app()
