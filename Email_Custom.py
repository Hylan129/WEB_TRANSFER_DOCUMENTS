#-*- coding : utf-8 -*-
import smtplib,re
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr
from email.mime.application import MIMEApplication

#检查邮件地址合法性
def verifyEmail(email):
    pattern = r'^[\.a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
    if re.match(pattern,email) is not None: return True
    else: return False

#添加邮件附件
def uploadPdf(path):
    """
    参数说明：path为本地图片路径,id_name为邮件附件呈现的附件名称，自己指定。
    """
    file_content = open(path,'rb')
    pdf_part = MIMEApplication(file_content.read())
    file_content.close()
    pdf_part.add_header('Content-Disposition', 'attachment', filename=path.split('/')[-1])
    
    #msgImage["Content-Disposition"] = 'attachment; filename="' + id_name +'.' + path.strip().split('.')[-1] + '"'
    return pdf_part

#添加图片编号
def uploadPicture(path,id_name):
    # 指定图片为当前目录
    fp = open(path, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    # 定义图片 ID，在 HTML 文本中引用
    msgImage.add_header('Content-ID', '<'+id_name+'>')
    msgImage["Content-Disposition"] = 'attachment; filename="' + id_name +'.jpeg"'
    return msgImage

#发送邮件
def sendEmail(email,password,email_subject,content_page,towhos,attach_paths):
    # 第三方 SMTP 服务
    mail_host="smtp.163.com"  #设置服务器
    mail_user= email   #用户名
    mail_pass= password   #口令 
    
    message = MIMEMultipart()
    sender = email
    receivers = formataddr(['上帝',towhos]) # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    message['From'] = formataddr(['早鸟有饭','jyzyg129@163.com'])
    message['To'] = receivers

    #添加设置邮件主题
    subject = email_subject
    message['Subject'] = Header(subject, 'utf-8')

    #添加设置邮件正文，网页表单。
    message.attach(MIMEText(content_page, 'html', 'utf-8'))

    message.attach(uploadPicture('webpage/feedback/thanksforyourpraise.jpeg','praise'))

    message.attach(uploadPdf(attach_paths))

    #邮件发送
    smtpObj = smtplib.SMTP_SSL(mail_host,465) 
    #smtpObj.connect(mail_host, 465)    #qq:465,163:25
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    
    
    return True
